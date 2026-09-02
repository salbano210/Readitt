# 🗣️ Readitt – Reddit Thread Reader with AI-Style Voices

**Readitt** is a voice-driven Python app that reads Reddit threads aloud like a conversation — using different text-to-speech voices for each commenter. Great for turning long threads into podcast-style audio. I came up with it while driving home from work, wishing I had more highly opinionated podcast content for my ride. I also wished it could be named by a guy who sometimes thinks that Reddit has two t's instead of two d's.

---

## 🎯 Features

- 🔁 Reads top-level Reddit comments from any public thread
- 🧑‍🎤 Each commenter is read in one of several expressive voices — you can tell speakers apart by voice alone, no announcements needed
- 🎭 **Consistent voice casting** — each Redditor keeps the same voice across threads and sessions (persisted in `~/.readitt/voices.json`, overridable with `--map`)
- 💾 **Save to a WAV file** with `--save` and listen on your commute, plus an estimated listening time before playback
- 🛠️ **Zero-friction onboarding** — `python main.py --setup` interactively configures your Reddit credentials, and friendly errors guide you through bad URLs, rate limits, and missing threads
- 🎙️ Uses `praw` for Reddit access and `pyttsx3`/`piper` for text-to-speech

---

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/readitt.git
cd readitt
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install praw pyttsx3 python-dotenv
```

### 4. Configure Reddit API Access

Create a `.env` file in the root of the project and add:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=readitt-script by u/your_username
```

> 🔑 You can get these by creating a Reddit script app:  
> https://www.reddit.com/prefs/apps

---

## ▶️ Usage

```bash
python main.py "https://www.reddit.com/r/someSub/comments/abc123/thread_title/" \
    --comments 5
```

Options:

- `-n/--comments N` — how many top-level comments to read (default: 5)
- `--engine auto|piper|pyttsx3` — TTS engine (default: `auto`, uses Piper if set up, otherwise pyttsx3)
- `--rate N` — speaking rate (pyttsx3 engine only, default: 185)
- `--models-dir PATH` — directory of Piper voice models (or set `PIPER_MODELS_DIR` in `.env`)
- `--max-chars N` — max characters spoken per comment (default: 300)
- `--sort best|top|new|controversial` — comment sort order (default: `best`)
- `--save FILE` — render the whole thread to a single `.wav` file instead of playing live (great for commutes — drop it in your podcast app)
- `--map SPEC` — pin specific voices, e.g. `--map 'u/jimmybob=Samantha,alice=Fred'`
- `--setup` — interactive walkthrough that saves your Reddit API credentials to `.env`
- `--list-voices` — print the voices available for the chosen engine

### 🎭 Voice casting

Every commenter gets a **consistent, deterministic voice**: `u/jimmybob` sounds the same every time you run Readitt, on any thread. Assignments are persisted to `~/.readitt/voices.json`, so voices survive even if your system voice list changes. To override the automatic casting:

```bash
# See what's available
python main.py --list-voices

# Pin a favorite voice to a commenter (persists across sessions)
python main.py <url> --map 'u/jimmybob=Samantha'
```

### 💾 Saving to an audio file

```bash
python main.py <thread-url> --save commute.wav
```

Readitt prints an estimated listening time up front, then writes the full thread to one WAV file you can copy to your phone.

### 🛠️ First-run setup

If you haven't configured Reddit credentials yet, just run:

```bash
python main.py --setup
```

It walks you through creating a Reddit script app at https://www.reddit.com/prefs/apps and writes `.env` for you.

### 🎙️ Voice engines

| Engine | Quality | Needs internet | Notes |
| --- | --- | --- | --- |
| `piper` | ⭐⭐⭐ neural | ❌ | `pip install piper-tts`, then download `.onnx` models from [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices) into a directory and set `PIPER_MODELS_DIR` in `.env` |
| `pyttsx3` | ⭐ robotic | ❌ | Uses built-in OS voices (macOS `say`, SAPI5, espeak). Zero setup fallback |

