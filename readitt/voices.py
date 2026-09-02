"""Persistent speaker→voice mapping and deterministic voice assignment.

Voice assignments are stored in ~/.readitt/voices.json so the same
Redditor keeps the same voice across sessions, even if the pool of
system voices changes between runs.
"""

import hashlib
import json
from pathlib import Path

VOICE_MAP_PATH = Path.home() / ".readitt" / "voices.json"


def load_voice_map(path: Path = VOICE_MAP_PATH) -> dict[str, str]:
    """Load saved speaker→voice assignments; missing/corrupt file → {}."""
    try:
        return {k: str(v) for k, v in json.loads(path.read_text()).items()}
    except (OSError, ValueError):
        return {}


def save_voice_map(mapping: dict[str, str], path: Path = VOICE_MAP_PATH) -> None:
    """Merge assignments into the on-disk voice map."""
    try:
        merged = load_voice_map(path)
        merged.update(mapping)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(merged, indent=2, sort_keys=True))
    except OSError:
        pass  # persistence is best-effort; never break playback


def parse_voice_overrides(spec: str) -> dict[str, str]:
    """Parse a --map spec like 'u/jimmybob=Samantha,alice=Fred'.

    Leading 'u/' is stripped from speaker keys so both forms work.
    """
    overrides: dict[str, str] = {}
    for pair in spec.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(
                f"Invalid --map entry {pair!r} — expected SPEAKER=VOICE, e.g. u/jimmybob=Samantha"
            )
        speaker, voice = (part.strip() for part in pair.split("=", 1))
        if not speaker or not voice:
            raise ValueError(
                f"Invalid --map entry {pair!r} — both speaker and voice are required"
            )
        overrides[speaker.removeprefix("u/")] = voice
    return overrides


def pick_voice(pool: list[str], speaker_key: str) -> str:
    """Deterministically pick a voice from the pool for a speaker.

    Uses an md5 digest of the speaker key so 'u/jimmybob' always gets the
    same voice, within a thread and across sessions.
    """
    digest = hashlib.md5(speaker_key.encode()).digest()
    return pool[digest[0] % len(pool)]