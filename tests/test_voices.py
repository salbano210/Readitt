import json

import pytest

from readitt import voices
from readitt.voices import (
    load_voice_map,
    parse_voice_overrides,
    pick_voice,
    save_voice_map,
)


class TestParseVoiceOverrides:
    def test_single_pair(self):
        assert parse_voice_overrides("u/jimmybob=Samantha") == {"jimmybob": "Samantha"}

    def test_u_prefix_optional(self):
        assert parse_voice_overrides("alice=Fred") == {"alice": "Fred"}

    def test_multiple_pairs_with_spaces(self):
        spec = "u/jimmybob=Samantha, alice=Fred"
        assert parse_voice_overrides(spec) == {"jimmybob": "Samantha", "alice": "Fred"}

    def test_missing_equals_raises(self):
        with pytest.raises(ValueError):
            parse_voice_overrides("no-equals-sign")

    def test_empty_side_raises(self):
        with pytest.raises(ValueError):
            parse_voice_overrides("=Samantha")
        with pytest.raises(ValueError):
            parse_voice_overrides("jimmybob=")

    def test_empty_entries_ignored(self):
        assert parse_voice_overrides(" , u/x=Eddy , ") == {"x": "Eddy"}


class TestPickVoice:
    def test_deterministic(self):
        pool = ["a", "b", "c"]
        assert pick_voice(pool, "jimmybob") == pick_voice(pool, "jimmybob")

    def test_always_in_pool(self):
        pool = ["a", "b", "c", "d"]
        for user in ["u1", "u2", "u3", "u4", "u5"]:
            assert pick_voice(pool, user) in pool

    def test_distribution_not_degenerate(self):
        pool = [f"v{i}" for i in range(10)]
        picks = {pick_voice(pool, f"user{i}") for i in range(50)}
        assert len(picks) > 3


class TestVoiceMapPersistence:
    def test_missing_file_returns_empty(self, tmp_path):
        assert load_voice_map(tmp_path / "nope.json") == {}

    def test_roundtrip(self, tmp_path):
        path = tmp_path / "voices.json"
        save_voice_map({"jimmybob": "Samantha"}, path)
        assert load_voice_map(path) == {"jimmybob": "Samantha"}

    def test_merges_not_overwrites(self, tmp_path):
        path = tmp_path / "voices.json"
        save_voice_map({"a": "1"}, path)
        save_voice_map({"b": "2"}, path)
        assert load_voice_map(path) == {"a": "1", "b": "2"}

    def test_corrupt_file_returns_empty(self, tmp_path):
        path = tmp_path / "voices.json"
        path.write_text("{not json")
        assert load_voice_map(path) == {}

    def test_default_path_is_in_home(self):
        assert voices.VOICE_MAP_PATH.name == "voices.json"
        assert ".readitt" in str(voices.VOICE_MAP_PATH)