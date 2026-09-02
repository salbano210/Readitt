"""pyttsx3 engine — the original, OS-native fallback (macOS `say`, SAPI5, espeak)."""

import tempfile
from pathlib import Path

from .base import TTSEngine
from readitt.voices import pick_voice

# Fun voice picks; fall back to any English voice if none of these exist.
_PREFERRED_VOICE_NAMES = [
    "Eddy", "Fred", "Grandma", "Karen", "Moira",
    "Ralph", "Reed", "Rishi", "Samantha", "Tessa",
]
_NARRATOR_NAME = "Daniel"


class Pyttsx3Engine(TTSEngine):
    name = "pyttsx3"

    def __init__(
        self,
        rate: int = 185,
        save_path: str | None = None,
        voice_map: dict[str, str] | None = None,
    ) -> None:
        import pyttsx3

        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)

        voices = self._engine.getProperty("voices")
        preferred = [v for v in voices if v.name in _PREFERRED_VOICE_NAMES]
        english = [
            v for v in voices if "en" in str(getattr(v, "languages", [""])[0]).lower()
        ]
        pool = preferred or english
        if not pool:
            raise RuntimeError("No English TTS voices found on this system.")

        self._pool_names = [v.name for v in pool]
        self._voices_by_name = {v.name: v for v in pool}
        self._speaker_assignments: dict[str, object] = {}
        self._voice_map = dict(voice_map or {})
        self._save_path = Path(save_path).expanduser() if save_path else None
        self._segments: list[Path] = []
        self._tmp_dir: Path | None = None

        narrator = next((v for v in voices if v.name == _NARRATOR_NAME), None)
        self._narrator_voice = narrator or pool[0]

    def _voice_for(self, speaker_key: str) -> object:
        if speaker_key not in self._speaker_assignments:
            key = speaker_key.removeprefix("u/")
            if key in self._voice_map and self._voice_map[key] in self._voices_by_name:
                voice = self._voices_by_name[self._voice_map[key]]
            else:
                name = pick_voice(self._pool_names, speaker_key)
                voice = self._voices_by_name[name]
            self._speaker_assignments[speaker_key] = voice
        return self._speaker_assignments[speaker_key]

    def speaker_voice_names(self) -> dict[str, str]:
        """Return the speaker→voice-name assignments made this run."""
        return {
            k.removeprefix("u/"): v.name for k, v in self._speaker_assignments.items()
        }

    def _say(self, voice: object, text: str) -> None:
        self._engine.setProperty("voice", voice.id)
        if self._save_path:
            if self._tmp_dir is None:
                self._tmp_dir = Path(tempfile.mkdtemp(prefix="readitt-"))
            segment = self._tmp_dir / f"seg_{len(self._segments):04d}.wav"
            self._engine.save_to_file(text, str(segment))
            self._engine.runAndWait()
            self._segments.append(segment)
        else:
            self._engine.say(text)
            self._engine.runAndWait()

    def speak_narrator(self, text: str) -> None:
        self._say(self._narrator_voice, text)

    def speak_comment(self, text: str, speaker_key: str) -> None:
        self._say(self._voice_for(speaker_key), text)

    def finalize(self) -> Path | None:
        """Combine all saved segments into the single output file."""
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
        try:
            self._engine.stop()
        except Exception:
            pass
