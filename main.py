# Readitt: Reddit thread reader with AI-style voice acting
# Built using praw (Reddit API) and pyttsx3 (text-to-speech)

import os
from pathlib import Path
from dotenv import load_dotenv

# Tell Python exactly where to find the .env file
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)
import praw
import pyttsx3
import random

# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty("voices")

# Tune speaking rate (optional tweak between 150–200)
engine.setProperty("rate", 185)

# 🎭 Commenter voices — your custom picks
preferred_voice_names = [
    "Eddy", "Fred", "Grandma", "Karen", "Moira",
    "Ralph", "Reed", "Rishi", "Samantha", "Tessa"
]

# Create a filtered list of voice IDs that match your picks
custom_voice_ids = [
    v.id for v in voices if v.name in preferred_voice_names
]

# Filter for English voices only
english_voices = [v for v in voices if "en" in str(v.languages[0]).lower()]
english_voice_ids = [v.id for v in english_voices]

# Pick 1 consistent narrator voice
narrator_voice_id = next(v.id for v in voices if v.name == "Daniel")


reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Load thread
url = "https://www.reddit.com/r/JaegerLecoultre/comments/1jwxg1r/polaris_or_chronograph_calendar/"
submission = reddit.submission(url=url)
submission.comments.replace_more(limit=0)

print("🧵", submission.title)
print()

# Read 5 comments aloud
for comment in submission.comments[:5]:
    author = str(comment.author) if comment.author else "Anonymous"
    text = comment.body.strip().replace("\n", " ")

    # Clean up formatting
    text = text.replace("&amp;", "&").replace("&#x200B;", "").replace("  ", " ")

    # Print to terminal
    print(f"{author}: {text[:150]}...\n")

    # Narrator voice: say who is speaking
    engine.setProperty("voice", narrator_voice_id)
    engine.say(f"{author} says:")

    # Commenter voice speaks
    comment_voice_id = random.choice(custom_voice_ids)
    engine.setProperty("voice", comment_voice_id)
    engine.say(text[:300])


    engine.runAndWait()
