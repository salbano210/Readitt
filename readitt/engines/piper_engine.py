"""Piper engine — fast, local neural TTS with genuinely distinct voices.

Requires `pip install piper-tts` plus downloaded voice models (.onnx + .json).
Point PIPER_MODELS_DIR at a directory of models, or pass --models-dir.
Get models at https://huggingface.co/rhasspy/piper-voices
"""

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .base import TTSEngine, _playback_command


def _find_models(models_dir: Path) -> list[Path]:
    if not models_dir.is_dir():
        raise FileNotFoundError(f"Piper models directory not found: {models_dir}")
    models = sorted(models_dir.glob("*.onnx"))
    if not models:
        raise FileNotFoundError(f"No .onnx voice models in {models_dir}")
    return models


class PiperEngine(TTSEngine):
    name = "piper"

    def __init__(
        self,
        models_dir: str | None = None,
        save_path: str | None = None,
        voice_map: dict[str, str] | None = None,
    ) -> None:
        from piper import PiperVoice  # noqa: deferred — optional dependency

        models_dir = Path(models_dir or os.getenv("PIPER_MODELS_DIR", "")).expanduser()
        model_paths = _find_models(models_dir)

        self._voices: dict[str, PiperVoice] = {}
        for path in model_paths:
            self._voices[path.stem] = PiperVoice.load(str(path))

        self._model_names = list(self._voices)
        self._speaker_assignments: dict[str, str] = {}
        self._voice_map = dict(voice_map or {})
        self._save_path = Path(save_path).expanduser() if save_path else None
        self._segments: list[Path] = []
        self._tmp_dir: Path | None = None

    def _model_for(self, speaker_key: str) -> str:
        """Deterministically assign a distinct model per speaker."""
        if speaker_key not in self._speaker_assignments:
            key = speaker_key.removeprefix("u/")
            if key in self._voice_map and self._voice_map[key] in self._voices:
                self._speaker_assignments[speaker_key] = self._voice_map[key]
            else:
                digest = hashlib.md5(speaker_key.encode()).digest()
                self._speaker_assignments[speaker_key] = self._model_names[
                    digest[0] % len(self._model_names)
                ]
        return self._speaker_assignments[speaker_key]

    def speaker_voice_names(self) -> dict[str, str]:
        """Return the speaker→voice-name assignments made this run."""
        return {k: v for k, v in self._speaker_assignments.items()}

    def _synthesize(self, text: str, model_name: str) -> Path:
        voice = self._voices[model_name]
        if self._save_path:
            if self._tmp_dir is None:
                self._tmp_dir = Path(tempfile.mkdtemp(prefix="readitt-"))
            out_path = self._tmp_dir
        else:
            out_path = Path(tempfile.mkdtemp(prefix="readitt-"))
        out_path.mkdir(parents=True, exist_ok=True)
        wav_path = out_path / f"{model_name}_{hashlib.md5(text.encode()).hexdigest()[:10]}.wav"
        with open(wav_path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        if self._save_path:
            self._segments.append(wav_path)
        return wav_path

    def _play(self, wav_path: Path) -> None:
        subprocess.run(_playback_command() + [str(wav_path)], check=True)

    def speak_narrator(self, text: str) -> None:
        # Narrator always uses the first model for a consistent "host" voice.
        wav_path = self._synthesize(text, self._model_names[0])
        if not self._save_path:
            self._play(wav_path)

    def speak_comment(self, text: str, speaker_key: str) -> None:
        model_name = self._model_for(speaker_key)
        wav_path = self._synthesize(text, model_name)
        if not self._save_path:
            self._play(wav_path)
            print(f"🎙️  {speaker_key} (voice: {model_name})")

    def finalize(self) -> Path | None:
        """Combine all recorded segments into the single output file."""
        if not self._save_path:
            return None
        from .base import combine_wavs

        try:
            combine_wavs(self._segments, self._save_path)
        except ValueError as exc:
            print(f"⚠️  Could not combine into one file: {exc}")
            print(f"    Individual segments are in {self._tmp_dir}")
            return None
        return self._save_path

    def close(self) -> None:
        pass


def piper_available() -> bool:
    """True if the piper package can be imported."""
    try:
        import piper  # noqa: F401
        return True
    except ImportError:
        return False


def piper_missing_help() -> str:
    return (
        "Piper engine unavailable. To use it:\n"
        "  1. pip install piper-tts\n"
        "  2. Download .onnx voice models (see .env.example / README)\n"
        "  3. Set PIPER_MODELS_DIR in .env to the models directory\n"
        f"(Python {sys.version.split()[0]} at {sys.executable})"
    )
