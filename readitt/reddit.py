from pathlib import Path
import re

import praw
import prawcore

# Matches a public Reddit thread URL, e.g.
# https://www.reddit.com/r/someSub/comments/abc123/thread_title/ or reddit.com/r/x/comments/abc123
_THREAD_URL_RE = re.compile(
    r"^https?://(?:www\.|old\.|new\.|np\.)?reddit\.com/r/[^/\s]+/comments/[a-z0-9]+",
    re.IGNORECASE,
)


def validate_thread_url(url: str) -> str:
    """Raise a friendly error unless url looks like a Reddit thread link."""
    if not _THREAD_URL_RE.match(url.strip()):
        raise SystemExit(
            "❌ That doesn't look like a Reddit thread URL.\n"
            "   Expected something like:\n"
            "   https://www.reddit.com/r/someSub/comments/abc123/thread_title/"
        )
    return url.strip()


def get_reddit() -> praw.Reddit:
    import os

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    missing = [
        name
        for name, value in [
            ("REDDIT_CLIENT_ID", client_id),
            ("REDDIT_CLIENT_SECRET", client_secret),
            ("REDDIT_USER_AGENT", user_agent),
        ]
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing Reddit credentials: "
            + ", ".join(missing)
            + ". Run `python main.py --setup` for an interactive walkthrough, "
            "or copy .env.example to .env and fill in your values "
            "(https://www.reddit.com/prefs/apps)."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def fetch_comments(
    url: str, limit: int = 5, sort: str = "best"
) -> tuple[str, list[dict]]:
    """Return (thread_title, [comment dicts]) for the top-level comments."""
    url = validate_thread_url(url)
    reddit = get_reddit()
    submission = reddit.submission(url=url)
    submission.comment_sort = sort
    try:
        submission.comments.replace_more(limit=0)
    except prawcore.exceptions.ResponseException as exc:
        if exc.response and exc.response.status_code == 429:
            raise SystemExit(
                "❌ Reddit is rate-limiting this app (HTTP 429). "
                "Wait a minute or two and try again."
            ) from exc
        raise SystemExit(
            f"❌ Reddit returned an error (HTTP {getattr(exc.response, 'status_code', '?')}). "
            "Check your .env credentials and that the thread is public."
        ) from exc
    except prawcore.exceptions.NotFound:
        raise SystemExit(
            "❌ That thread couldn't be found — it may have been deleted, "
            "made private, or the URL may be mistyped."
        ) from None
    except prawcore.exceptions.RequestException as exc:
        raise SystemExit(
            f"❌ Couldn't reach Reddit ({exc.__class__.__name__}). "
            "Check your internet connection and try again."
        ) from exc

    if not submission.comments:
        raise SystemExit(
            "❌ No comments found in that thread (they may all have been deleted, "
            "or the subreddit may block this app)."
        )

    comments = []
    for comment in submission.comments[:limit]:
        comments.append(
            {
                "author": str(comment.author) if comment.author else "Anonymous",
                "body": comment.body,
            }
        )
    return submission.title, comments
