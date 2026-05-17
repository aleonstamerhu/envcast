"""Tests for envcast.filterer."""

import pytest

from envcast.filterer import FilterEntry, FilterResult, filter_env


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "secret",
        "APP_NAME": "envcast",
        "DEBUG": "true",
    }


def test_filter_returns_filter_result(sample_env):
    result = filter_env(sample_env, prefix="DB_")
    assert isinstance(result, FilterResult)


def test_filter_entry_count_matches_env(sample_env):
    result = filter_env(sample_env, prefix="DB_")
    assert len(result.entries) == len(sample_env)


def test_filter_by_prefix_matches_correct_keys(sample_env):
    result = filter_env(sample_env, prefix="DB_")
    matched_keys = {e.key for e in result.entries if e.matched}
    assert matched_keys == {"DB_HOST", "DB_PORT"}


def test_filter_by_prefix_reason_label(sample_env):
    result = filter_env(sample_env, prefix="AWS_")
    for entry in result.entries:
        if entry.matched:
            assert entry.reason == "prefix"


def test_filter_by_pattern_glob(sample_env):
    result = filter_env(sample_env, pattern="AWS_*")
    matched_keys = {e.key for e in result.entries if e.matched}
    assert matched_keys == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_filter_by_pattern_reason_label(sample_env):
    result = filter_env(sample_env, pattern="DB_*")
    for entry in result.entries:
        if entry.matched:
            assert entry.reason == "pattern"


def test_filter_by_regex(sample_env):
    result = filter_env(sample_env, regex=r"^(DB|AWS)_")
    matched_keys = {e.key for e in result.entries if e.matched}
    assert matched_keys == {"DB_HOST", "DB_PORT", "AWS_ACCESS_KEY", "AWS_SECRET"}


def test_filter_by_regex_reason_label(sample_env):
    result = filter_env(sample_env, regex=r"PORT$")
    for entry in result.entries:
        if entry.matched:
            assert entry.reason == "regex"


def test_filter_by_predicate(sample_env):
    result = filter_env(sample_env, predicate=lambda k, v: v.isdigit())
    matched_keys = {e.key for e in result.entries if e.matched}
    assert matched_keys == {"DB_PORT"}


def test_filter_predicate_reason_label(sample_env):
    result = filter_env(sample_env, predicate=lambda k, v: len(v) > 5)
    for entry in result.entries:
        if entry.matched:
            assert entry.reason == "predicate"


def test_filter_no_criteria_matches_nothing(sample_env):
    result = filter_env(sample_env)
    assert result.matched_count == 0
    assert all(e.reason == "none" for e in result.entries)


def test_filtered_env_include_mode(sample_env):
    result = filter_env(sample_env, prefix="DB_", mode="include")
    env = result.filtered_env()
    assert set(env.keys()) == {"DB_HOST", "DB_PORT"}


def test_filtered_env_exclude_mode(sample_env):
    result = filter_env(sample_env, prefix="DB_", mode="exclude")
    env = result.filtered_env()
    assert "DB_HOST" not in env
    assert "DB_PORT" not in env
    assert "APP_NAME" in env


def test_invalid_mode_raises(sample_env):
    with pytest.raises(ValueError, match="mode must be"):
        filter_env(sample_env, prefix="DB_", mode="keep")


def test_has_matches_true_when_prefix_found(sample_env):
    result = filter_env(sample_env, prefix="APP_")
    assert result.has_matches is True


def test_has_matches_false_when_no_prefix_found(sample_env):
    result = filter_env(sample_env, prefix="NONEXISTENT_")
    assert result.has_matches is False
