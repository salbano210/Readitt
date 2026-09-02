import pytest

from readitt.text import clean_text, truncate_for_speech


class TestCleanText:
    def test_html_entities(self):
        assert clean_text("Fish &amp; chips") == "Fish & chips"

    def test_zero_width_space_removed(self):
        assert clean_text("hello&#x200B;world") == "helloworld"

    def test_markdown_link_keeps_label(self):
        assert clean_text("[check this](https://example.com)") == "check this"

    def test_bold_italic_stripped(self):
        assert clean_text("**so** *wrong*") == "so wrong"

    def test_username_prefix_removed(self):
        assert clean_text("u/jimmybob says no") == "jimmybob says no"

    def test_whitespace_collapsed(self):
        assert clean_text("line one\nline  two") == "line one line two"

    def test_quote_and_heading_stripped(self):
        assert clean_text("# Title\n&gt; quoted") == "Title quoted"


class TestTruncateForSpeech:
    def test_short_text_unchanged(self):
        assert truncate_for_speech("short", 300) == "short"

    def test_truncates_on_sentence_boundary(self):
        text = "First sentence. " + "x" * 400
        result = truncate_for_speech(text, 300)
        assert result == "First sentence."

    def test_truncates_on_word_boundary(self):
        text = "word " * 100
        result = truncate_for_speech(text.rstrip(), 300)
        assert result.endswith("word")
        assert len(result) <= 300

    def test_exact_length_unchanged(self):
        text = "a" * 300
        assert truncate_for_speech(text, 300) == text

    def test_no_boundaries_hard_truncates(self):
        text = "a" * 500
        assert truncate_for_speech(text, 300) == "a" * 300
