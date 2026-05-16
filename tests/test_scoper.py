"""Tests for envcast.scoper."""

import pytest
from envcast.scoper import ScopeEntry, ScopeResult, scope_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "secret",
        "APP_NAME": "envcast",
        "DEBUG": "true",
    }


def test_scope_env_returns_scope_result(sample_env):
    result = scope_env(sample_env, ["DB"])
    assert isinstance(result, ScopeResult)


def test_scope_entry_count_matches_env(sample_env):
    result = scope_env(sample_env, ["DB"])
    assert len(result.entries) == len(sample_env)


def test_scope_matches_prefix(sample_env):
    result = scope_env(sample_env, ["DB"])
    assert result.matched_count() == 2


def test_scope_matched_keys_correct(sample_env):
    result = scope_env(sample_env, ["DB"])
    matched = result.scoped_env()
    assert "DB_HOST" in matched
    assert "DB_PORT" in matched


def test_scope_unmatched_count(sample_env):
    result = scope_env(sample_env, ["DB"])
    assert result.unmatched_count() == 4


def test_scope_multiple_prefixes(sample_env):
    result = scope_env(sample_env, ["DB", "AWS"])
    assert result.matched_count() == 4


def test_scope_has_matches_true(sample_env):
    result = scope_env(sample_env, ["DB"])
    assert result.has_matches() is True


def test_scope_has_matches_false(sample_env):
    result = scope_env(sample_env, ["NOPE"])
    assert result.has_matches() is False


def test_scope_case_insensitive_by_default(sample_env):
    result = scope_env(sample_env, ["db"])
    assert result.matched_count() == 2


def test_scope_case_sensitive_no_match(sample_env):
    result = scope_env(sample_env, ["db"], case_sensitive=True)
    assert result.matched_count() == 0


def test_scope_case_sensitive_match(sample_env):
    result = scope_env(sample_env, ["DB"], case_sensitive=True)
    assert result.matched_count() == 2


def test_stripped_env_removes_prefix(sample_env):
    result = scope_env(sample_env, ["DB"])
    stripped = result.stripped_env()
    assert "HOST" in stripped
    assert "PORT" in stripped
    assert stripped["HOST"] == "localhost"


def test_scopes_requested_stored(sample_env):
    result = scope_env(sample_env, ["DB", "AWS"])
    assert result.scopes_requested == ["DB", "AWS"]


def test_exact_prefix_match_without_underscore(sample_env):
    env = {"DB": "main", "DB_HOST": "localhost"}
    result = scope_env(env, ["DB"])
    assert result.matched_count() == 2


def test_scope_entry_scope_field_set(sample_env):
    result = scope_env(sample_env, ["DB"])
    for entry in result.entries:
        if entry.key.startswith("DB_"):
            assert entry.scope == "DB"
        else:
            assert entry.scope is None
