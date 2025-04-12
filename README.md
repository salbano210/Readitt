# 🗣️ Readitt – Reddit Thread Reader with AI-Style Voices

**Readitt** is a voice-driven Python app that reads Reddit threads aloud like a conversation — using different text-to-speech voices for each commenter. Great for turning long threads into podcast-style audio. I came up with it while driving home from work, wishing I had more highly opinionated podcast content for my ride. I also wished it could be named by a guy who sometimes thinks that Reddit has two t's instead of two d's.

---

## 🎯 Features

- 🔁 Reads top-level Reddit comments from any public thread
- 🧑‍🏫 Narrator voice introduces each speaker (e.g., “u/jimmybob says…”)
- 🧑‍🎤 Comment content is read in one of several expressive voices
- 🎙️ Uses `praw` for Reddit access and `pyttsx3` for text-to-speech
- 🧪 Fully local — no external APIs or internet required to run

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

Open `main.py
