import pytest

from readitt.reddit import validate_thread_url


class TestValidateThreadUrl:
    def test_valid_url_passthrough(self):
        url = "https://www.reddit.com/r/someSub/comments/abc123/thread_title/"
        assert validate_thread_url(url) == url

    def test_valid_url_without_subdomain(self):
        assert validate_thread_url("http://reddit.com/r/x/comments/abc123")

    def test_valid_url_old_reddit(self):
        assert validate_thread_url("https://old.reddit.com/r/x/comments/abc123/hi")

    def test_strips_whitespace(self):
        url = "  https://www.reddit.com/r/x/comments/abc123/  "
        assert validate_thread_url(url).endswith("/")

    def test_rejects_subreddit_url(self):
        with pytest.raises(SystemExit):
            validate_thread_url("https://www.reddit.com/r/programming/")

    def test_rejects_garbage(self):
        with pytest.raises(SystemExit):
            validate_thread_url("not a url at all")

    def test_rejects_missing_thread_id(self):
        with pytest.raises(SystemExit):
            validate_thread_url("https://www.reddit.com/r/x/comments/")