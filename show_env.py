import os
from dotenv import load_dotenv
from pathlib import Path

# Force-load the .env file explicitly
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)

# Print everything Python sees as environment variables
for key in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]:
    print(f"{key} =", os.getenv(key))