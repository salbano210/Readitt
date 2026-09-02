from pathlib import Path

from .base import TTSEngine
from .pyttsx3_engine import Pyttsx3Engine

__all__ = ["TTSEngine", "Pyttsx3Engine", "create_engine", "list_engine_voice_names"]


def list_engine_voice_names(engine_name: str = "auto") -> list[str]:
    """Return the human-readable voice names available for an engine."""
    if engine_name == "piper":
        import os

        from .piper_engine import PiperEngine, piper_available, piper_missing_help

        if not piper_available():
            raise SystemExit(piper_missing_help())
        models_dir = Path(os.getenv("PIPER_MODELS_DIR", "")).expanduser()
        return [p.stem for p in sorted(models_dir.glob("*.onnx"))]
    from pyttsx3 import init

    voices = init().getProperty("voices")
    return [v.name for v in voices]


def create_engine(
    engine_name: str = "auto",
    rate: int = 185,
    models_dir: str | None = None,
    save_path: str | None = None,
    voice_map: dict[str, str] | None = None,
) -> TTSEngine:
    """Build a TTS engine by name, with graceful fallbacks.

    - auto: Piper if available, otherwise pyttsx3
    - piper: local neural TTS (requires piper-tts + models)
    - pyttsx3: OS-native voices
    """
    if engine_name in ("auto", "piper"):
        from .piper_engine import PiperEngine, piper_available, piper_missing_help

        try:
            if not piper_available():
                raise ImportError(piper_missing_help())
            if engine_name == "piper":
                return PiperEngine(
                    models_dir=models_dir, save_path=save_path, voice_map=voice_map
                )
            # auto: try Piper, fall back quietly if models aren't set up
            try:
                return PiperEngine(
                    models_dir=models_dir, save_path=save_path, voice_map=voice_map
                )
            except FileNotFoundError as exc:
                print(f"⚠️  Piper not set up ({exc}); falling back to pyttsx3.")
        except ImportError as exc:
            if engine_name == "piper":
                raise SystemExit(str(exc))
            print(f"⚠️  Piper unavailable; falling back to pyttsx3. ({exc})")

    return Pyttsx3Engine(rate=rate, save_path=save_path, voice_map=voice_map)
