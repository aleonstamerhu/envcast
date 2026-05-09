"""Tests for envcast.differ module."""

import pytest

from envcast.differ import diff_envs, DiffResult


@pytest.fixture
def source_env():
    return {"APP_ENV": "production", "DB_HOST": "prod-db", "SECRET": "abc123", "PORT": "8080"}


@pytest.fixture
def target_env():
    return {"APP_ENV": "staging", "DB_HOST": "prod-db", "DEBUG": "true", "PORT": "8080"}


def test_diff_detects_only_in_source(source_env, target_env):
    result = diff_envs(source_env, target_env)
    assert "SECRET" in result.only_in_source
    assert result.only_in_source["SECRET"] == "abc123"


def test_diff_detects_only_in_target(source_env, target_env):
    result = diff_envs(source_env, target_env)
    assert "DEBUG" in result.only_in_target
    assert result.only_in_target["DEBUG"] == "true"


def test_diff_detects_changed_values(source_env, target_env):
    result = diff_envs(source_env, target_env)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("production", "staging")


def test_diff_detects_matching_values(source_env, target_env):
    result = diff_envs(source_env, target_env)
    assert "DB_HOST" in result.matching
    assert "PORT" in result.matching


def test_diff_has_differences_true(source_env, target_env):
    result = diff_envs(source_env, target_env)
    assert result.has_differences is True


def test_diff_has_differences_false():
    env = {"KEY": "value"}
    result = diff_envs(env, env.copy())
    assert result.has_differences is False


def test_diff_respects_ignore_keys(source_env, target_env):
    result = diff_envs(source_env, target_env, ignore_keys=["APP_ENV", "SECRET", "DEBUG"])
    assert "APP_ENV" not in result.changed
    assert "SECRET" not in result.only_in_source
    assert "DEBUG" not in result.only_in_target


def test_diff_all_keys_union(source_env, target_env):
    result = diff_envs(source_env, target_env)
    expected = set(source_env) | set(target_env)
    assert result.all_keys == expected


def test_diff_empty_envs():
    result = diff_envs({}, {})
    assert not result.has_differences
    assert result.all_keys == set()


def test_diff_ignore_keys_does_not_affect_matching(source_env, target_env):
    """Keys in ignore_keys should not appear in any result category, including matching."""
    result = diff_envs(source_env, target_env, ignore_keys=["DB_HOST", "PORT"])
    assert "DB_HOST" not in result.matching
    assert "PORT" not in result.matching
