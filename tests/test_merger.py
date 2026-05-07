"""Tests for envcast.merger."""

import pytest

from envcast.merger import MergeResult, merge_envs


@pytest.fixture()
def base_env() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "false"}


@pytest.fixture()
def override_env() -> dict:
    return {"DB_HOST": "prod-db.example.com", "LOG_LEVEL": "info"}


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

def test_merge_combines_unique_keys(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert "DB_PORT" in result.merged
    assert "LOG_LEVEL" in result.merged


def test_merge_last_wins_by_default(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert result.merged["DB_HOST"] == "prod-db.example.com"


def test_merge_first_wins_strategy(base_env, override_env):
    result = merge_envs(
        [("base", base_env), ("override", override_env)],
        strategy="first-wins",
    )
    assert result.merged["DB_HOST"] == "localhost"


def test_merge_preserves_non_conflicting_keys(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert result.merged["DEBUG"] == "false"
    assert result.merged["DB_PORT"] == "5432"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_merge_detects_conflict(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert result.has_conflicts
    assert "DB_HOST" in result.conflicts


def test_merge_no_conflict_when_values_equal():
    env_a = {"KEY": "same"}
    env_b = {"KEY": "same"}
    result = merge_envs([("a", env_a), ("b", env_b)])
    assert not result.has_conflicts


def test_merge_conflict_count(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert result.conflict_count == 1


def test_merge_conflict_records_both_values(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    labels = [label for label, _ in result.conflicts["DB_HOST"]]
    assert "base" in labels
    assert "override" in labels


# ---------------------------------------------------------------------------
# sources_used
# ---------------------------------------------------------------------------

def test_merge_tracks_sources_used(base_env, override_env):
    result = merge_envs([("base", base_env), ("override", override_env)])
    assert result.sources_used == ["base", "override"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_merge_empty_sources():
    result = merge_envs([])
    assert result.merged == {}
    assert not result.has_conflicts


def test_merge_single_source(base_env):
    result = merge_envs([("only", base_env)])
    assert result.merged == base_env
    assert not result.has_conflicts


def test_merge_invalid_strategy(base_env):
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([("base", base_env)], strategy="random")


def test_merge_three_sources_last_wins():
    a = {"X": "1"}
    b = {"X": "2"}
    c = {"X": "3"}
    result = merge_envs([("a", a), ("b", b), ("c", c)])
    assert result.merged["X"] == "3"
