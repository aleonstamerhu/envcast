"""Tests for envcast.normalizer."""

import pytest
from envcast.normalizer import NormalizeEntry, NormalizeResult, normalize_env


@pytest.fixture()
def sample_env():
    return {
        "db_host": "localhost",
        "DB_PORT": "5432",
        "api key": "  abc123  ",
        "SECRET_TOKEN": "  mysecret",
        "CLEAN_KEY": "cleanvalue",
    }


def test_normalize_returns_normalize_result(sample_env):
    result = normalize_env(sample_env)
    assert isinstance(result, NormalizeResult)


def test_normalize_entry_count_matches_env(sample_env):
    result = normalize_env(sample_env)
    assert result.key_count() == len(sample_env)


def test_uppercase_keys(sample_env):
    result = normalize_env(sample_env, uppercase_keys=True)
    assert "DB_HOST" in result.env
    assert "db_host" not in result.env


def test_uppercase_key_entry_marks_key_changed(sample_env):
    result = normalize_env(sample_env, uppercase_keys=True)
    entry = next(e for e in result.entries if e.original_key == "db_host")
    assert entry.key_changed is True
    assert entry.key == "DB_HOST"


def test_already_uppercase_key_not_marked_changed(sample_env):
    result = normalize_env(sample_env, uppercase_keys=True)
    entry = next(e for e in result.entries if e.original_key == "DB_PORT")
    assert entry.key_changed is False


def test_spaces_in_key_replaced(sample_env):
    result = normalize_env(sample_env, replace_spaces_in_keys=True)
    assert "API_KEY" in result.env


def test_spaces_in_key_entry_marks_key_changed(sample_env):
    result = normalize_env(sample_env, replace_spaces_in_keys=True)
    entry = next(e for e in result.entries if e.original_key == "api key")
    assert entry.key_changed is True


def test_strip_values_removes_whitespace(sample_env):
    result = normalize_env(sample_env, strip_values=True)
    assert result.env.get("API_KEY") == "abc123"


def test_strip_value_marks_value_changed(sample_env):
    result = normalize_env(sample_env, strip_values=True)
    entry = next(e for e in result.entries if e.original_key == "api key")
    assert entry.value_changed is True
    assert entry.normalized_value == "abc123"


def test_clean_value_not_marked_changed(sample_env):
    result = normalize_env(sample_env, strip_values=True)
    entry = next(e for e in result.entries if e.original_key == "CLEAN_KEY")
    assert entry.value_changed is False


def test_has_changes_true_when_something_changed(sample_env):
    result = normalize_env(sample_env)
    assert result.has_changes() is True


def test_has_changes_false_when_already_normalized():
    env = {"DB_HOST": "localhost", "API_PORT": "8080"}
    result = normalize_env(env)
    assert result.has_changes() is False


def test_changed_count_correct(sample_env):
    result = normalize_env(sample_env)
    changed = sum(1 for e in result.entries if e.was_changed)
    assert result.changed_count() == changed


def test_no_uppercase_leaves_keys_lowercase():
    env = {"db_host": "localhost"}
    result = normalize_env(env, uppercase_keys=False)
    assert "db_host" in result.env


def test_custom_space_replacement():
    env = {"my key": "value"}
    result = normalize_env(env, replace_spaces_in_keys=True, space_replacement="-")
    assert "MY-KEY" in result.env
