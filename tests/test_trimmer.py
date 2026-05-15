"""Tests for envcast.trimmer."""
import pytest
from envcast.trimmer import trim_env, TrimResult, TrimEntry


@pytest.fixture
def sample_env():
    return {
        "CLEAN_KEY": "no_whitespace",
        "LEADING": "  leading_space",
        "TRAILING": "trailing_space   ",
        "BOTH": "  both sides  ",
        "EMPTY": "",
        "ONLY_SPACES": "   ",
    }


def test_trim_returns_trim_result(sample_env):
    result = trim_env(sample_env)
    assert isinstance(result, TrimResult)


def test_trim_entry_count_matches_env(sample_env):
    result = trim_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_trim_clean_value_unchanged(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "CLEAN_KEY")
    assert entry.trimmed == "no_whitespace"
    assert not entry.was_trimmed


def test_trim_leading_whitespace(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "LEADING")
    assert entry.trimmed == "leading_space"
    assert entry.was_trimmed


def test_trim_trailing_whitespace(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "TRAILING")
    assert entry.trimmed == "trailing_space"
    assert entry.was_trimmed


def test_trim_both_sides(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "BOTH")
    assert entry.trimmed == "both sides"
    assert entry.was_trimmed


def test_trim_empty_value_unchanged(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "EMPTY")
    assert entry.trimmed == ""
    assert not entry.was_trimmed


def test_trim_only_spaces_becomes_empty(sample_env):
    result = trim_env(sample_env)
    entry = next(e for e in result.entries if e.key == "ONLY_SPACES")
    assert entry.trimmed == ""
    assert entry.was_trimmed


def test_trimmed_count(sample_env):
    result = trim_env(sample_env)
    # LEADING, TRAILING, BOTH, ONLY_SPACES => 4 trimmed
    assert result.trimmed_count == 4


def test_has_changes_true(sample_env):
    result = trim_env(sample_env)
    assert result.has_changes is True


def test_has_changes_false_when_all_clean():
    result = trim_env({"A": "clean", "B": "also_clean"})
    assert result.has_changes is False


def test_clean_count(sample_env):
    result = trim_env(sample_env)
    assert result.clean_count == len(sample_env) - result.trimmed_count


def test_env_dict_contains_trimmed_values(sample_env):
    result = trim_env(sample_env)
    assert result.env["LEADING"] == "leading_space"
    assert result.env["TRAILING"] == "trailing_space"
    assert result.env["BOTH"] == "both sides"
    assert result.env["CLEAN_KEY"] == "no_whitespace"


def test_trim_empty_env():
    result = trim_env({})
    assert result.entries == []
    assert result.env == {}
    assert result.trimmed_count == 0
    assert not result.has_changes
