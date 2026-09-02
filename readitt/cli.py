"""Readitt CLI — read a Reddit thread aloud like a podcast."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above this package)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .engines import create_engine, list_engine_voice_names
from .reddit import fetch_comments
from .text import clean_text, truncate_for_speech
from .voices import load_voice_map, parse_voice_overrides, save_voice_map

ENGINES = ["auto", "piper", "pyttsx3"]
SORTS = ["best", "top", "new", "controversial"]
WORDS_PER_MINUTE = 150  # rough estimate for the listening-time hint


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="readitt",
        description="Read a Reddit thread aloud with a different voice per commenter.",
    )
    parser.add_argument(
        "url", nargs="?", default=None, help="URL of a public Reddit thread"
    )
    parser.add_argument("--setup", action="store_true",
                        help="interactive setup: configure Reddit API credentials in .env")
    parser.add_argument("--list-voices", action="store_true",
                        help="list available TTS voices for the chosen engine and exit")
    parser.add_argument("-n", "--comments", type=int, default=5,
                        help="number of top-level comments to read (default: 5)")
    parser.add_argument("--rate", type=int, default=185,
                        help="speaking rate for pyttsx3 engine (default: 185)")
    parser.add_argument("--engine", choices=ENGINES, default="auto",
                        help="TTS engine (default: auto — Piper if set up, else pyttsx3)")
    parser.add_argument("--models-dir", default=None,
                        help="directory of Piper .onnx voice models (or set PIPER_MODELS_DIR)")
    parser.add_argument("--max-chars", type=int, default=300,
                        help="max characters spoken per comment (default: 300)")
    parser.add_argument("--sort", choices=SORTS, default="best",
                        help="comment sort order (default: best)")
    parser.add_argument("--save", default=None, metavar="FILE",
                        help="save the whole thread as one WAV file instead of playing live")
    parser.add_argument("--map", default=None, metavar="SPEC",
                        help="pin voices, e.g. --map 'u/jimmybob=Samantha,alice=Fred'")
    return parser


def run_setup(env_path: Path) -> int:
    """Interactive walkthrough that writes Reddit credentials to .env."""
    print("👋 Welcome to Readitt! Let's set up your Reddit API credentials.\n")
    print("1. Open https://www.reddit.com/prefs/apps")
    print("2. Scroll down and click 'create another app...'")
    print("3. Choose 'script', name it readitt, and use http://localhost:8080")
    print("   as the redirect URI.\n")

    existing: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, _, value = line.partition("=")
                existing[key.strip()] = value.strip()

    fields = [
        ("REDDIT_CLIENT_ID", "your app's client id (under the app name)"),
        ("REDDIT_CLIENT_SECRET", "your app's secret"),
        ("REDDIT_USER_AGENT", "a user agent, e.g. readitt-script by u/your_username"),
    ]
    values = dict(existing)
    for key, hint in fields:
        current = values.get(key, "")
        suffix = f" [current: {current}]" if current else ""
        answer = input(f"{key} ({hint}){suffix}: ").strip()
        if answer:
            values[key] = answer

    lines = [f"{key}={values.get(key, '')}" for key, _ in fields]
    if existing.get("PIPER_MODELS_DIR"):
        lines.append(f"PIPER_MODELS_DIR={existing['PIPER_MODELS_DIR']}")
    env_path.write_text("\n".join(lines) + "\n")

    print(f"\n✅ Saved credentials to {env_path}")
    print("   You're ready to go: python main.py <thread-url>")
    return 0


def _format_duration(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs:02d}s"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    env_path = Path(__file__).resolve().parent.parent / ".env"

    if args.setup:
        return run_setup(env_path)

    if args.list_voices:
        try:
            names = list_engine_voice_names(args.engine)
        except SystemExit:
            raise
        except Exception as exc:
            print(f"❌ Could not list voices: {exc}", file=sys.stderr)
            return 1
        print(f"🎙️  Voices available for the {args.engine} engine:")
        for name in names:
            print(f"  - {name}")
        print("\nPin one with: --map 'u/someuser=NAME'")
        return 0

    if not args.url:
        print("❌ Missing thread URL. Usage: readitt <thread-url>", file=sys.stderr)
        return 2

    voice_map = load_voice_map()
    if args.map:
        try:
            voice_map.update(parse_voice_overrides(args.map))
        except ValueError as exc:
            print(f"❌ {exc}", file=sys.stderr)
            return 2

    try:
        title, comments = fetch_comments(args.url, limit=args.comments, sort=args.sort)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"❌ Failed to fetch the thread: {exc}", file=sys.stderr)
        return 1

    print("🧵", title)
    print()

    prepared = []
    total_words = 0
    for comment in comments:
        author = comment["author"]
        body = truncate_for_speech(clean_text(comment["body"]), args.max_chars)
        if not body or body in {"[removed]", "[deleted]"}:
            continue
        total_words += len(body.split())
        prepared.append((author, body))

    if not prepared:
        print("Nothing readable in that thread — all comments were empty or removed.")
        return 0

    estimate = total_words / WORDS_PER_MINUTE * 60 + len(prepared) * 2
    suffix = " (audio file)" if args.save else ""
    print(f"🎙️  {len(prepared)} comments · estimated listening time: "
          f"{_format_duration(estimate)}{suffix}\n")

    engine = create_engine(
        engine_name=args.engine,
        rate=args.rate,
        models_dir=args.models_dir,
        save_path=args.save,
        voice_map=voice_map,
    )
    print(f"🎙️  Using {engine.name} engine\n")

    try:
        for author, body in prepared:
            print(f"{author}: {body[:150]}{'…' if len(body) > 150 else ''}\n")
            engine.speak_narrator(f"{author} says:")
            engine.speak_comment(body, author)
    except KeyboardInterrupt:
        print("\n👋 Stopped.")
        return 130
    finally:
        try:
            engine.close()
        except Exception:
            pass

    saved = engine.finalize() if hasattr(engine, "finalize") else None
    if saved:
        print(f"💾 Saved thread audio to {saved}")

    # Persist this run's speaker→voice assignments for future sessions.
    if hasattr(engine, "speaker_voice_names"):
        assignments = engine.speaker_voice_names()
        if assignments:
            save_voice_map(assignments)
            print("🎭 Voice cast saved to ~/.readitt/voices.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
