"""TTSEngine abstraction: each engine handles narrator + per-speaker voices."""

from pathlib import Path


class TTSEngine:
    """Base class for text-to-speech engines.

    Engines assign a distinct, consistent voice to each speaker key
    (e.g. a Reddit username) so a thread sounds like a conversation.
    """

    name = "base"

    def speak_narrator(self, text: str) -> None:
        """Speak an intro line in the narrator voice."""
        raise NotImplementedError

    def speak_comment(self, text: str, speaker_key: str) -> None:
        """Speak comment text in the voice assigned to speaker_key."""
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - default no-op
        pass


def combine_wavs(paths: list[Path], out_path: Path) -> Path:
    """Concatenate WAV files with identical audio params into out_path.

    Raises ValueError if segments have mismatched sample rates / widths,
    so callers can fall back to telling the user where segments live.
    """
    if not paths:
        raise ValueError("No audio segments to combine.")
    import wave

    with wave.open(str(paths[0]), "rb") as first:
        params = first.getparams()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as out:
        out.setparams(params)
        for path in paths:
            try:
                with wave.open(str(path), "rb") as seg:
                    if (
                        seg.getnchannels() != params.nchannels
                        or seg.getsampwidth() != params.sampwidth
                        or seg.getframerate() != params.framerate
                    ):
                        raise ValueError(
                            f"Mismatched audio format in {path.name}; cannot combine."
                        )
                    out.writeframes(seg.readframes(seg.getnframes()))
            except wave.Error as exc:
                raise ValueError(f"Corrupt or unreadable WAV segment {path.name}: {exc}") from exc
    return out_path


def _playback_command() -> list[str]:
    """Return the shell command used to play a WAV file on this platform."""
    import shutil
    import sys

    if sys.platform == "darwin":
        player = shutil.which("afplay")
    else:
        player = shutil.which("paplay") or shutil.which("aplay")
    if not player:
        raise RuntimeError("No WAV player found (tried afplay/paplay/aplay).")
    return [player]
