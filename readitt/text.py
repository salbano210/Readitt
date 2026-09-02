"""Text cleanup helpers for converting Reddit comments into speech."""

import re

_HTML_ENTITIES = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&#x200B;": "",
    "&nbsp;": " ",
}

_MARKDOWN_PATTERNS = [
    (re.compile(r"!?\[([^\]]*)\]\([^)]*\)"), r"\1"),  # links / images -> text
    (re.compile(r"\*\*?([^*]+)\*\*?"), r"\1"),        # bold / italic
    (re.compile(r"^(&gt;|>)\s?", re.MULTILINE), ""),  # quotes
    (re.compile(r"^#{1,6}\s?", re.MULTILINE), ""),    # headings
    (re.compile(r"^\s*[-*]\s", re.MULTILINE), ""),    # list bullets
    (re.compile(r"/?u/([A-Za-z0-9_-]+)"), r"\1"),     # u/username -> name
]


def clean_text(text: str) -> str:
    """Strip Reddit formatting and HTML entities so text sounds natural."""
    for entity, replacement in _HTML_ENTITIES.items():
        text = text.replace(entity, replacement)
    for pattern, replacement in _MARKDOWN_PATTERNS:
        text = pattern.sub(replacement, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_for_speech(text: str, max_chars: int = 300) -> str:
    """Truncate on a sentence or word boundary, never mid-word."""
    if len(text) <= max_chars:
        return text
    window = text[: max_chars + 1]
    # Prefer the end of the last complete sentence in the window.
    sentence_end = max(window.rfind(". "), window.rfind("! "), window.rfind("? "))
    if sentence_end > 0:
        return text[: sentence_end + 1]
    # Fall back to the last complete word.
    space_end = window.rfind(" ")
    if space_end > 0:
        return text[:space_end]
    return text[:max_chars]
