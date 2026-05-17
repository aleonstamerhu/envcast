"""Tests for envcast.flattener and envcast.flatten_formatter."""
from __future__ import annotations

import pytest

from envcast.flattener import FlattenEntry, FlattenResult, flatten_env
from envcast.flatten_formatter import format_flatten


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB__HOST": "localhost",
        "DB__PORT": "5432",
        "APP__SECRET_KEY": "s3cr3t",
        "PLAIN_KEY": "value",
    }


# ---------------------------------------------------------------------------
# flatten_env — basic behaviour
# ---------------------------------------------------------------------------

def test_flatten_returns_flatten_result(sample_env):
    result = flatten_env(sample_env)
    assert isinstance(result, FlattenResult)


def test_flatten_entry_count_matches_env(sample_env):
    result = flatten_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_flatten_double_underscore_renamed(sample_env):
    result = flatten_env(sample_env)
    renamed = {e.original_key for e in result.entries if e.was_renamed}
    assert "DB__HOST" in renamed
    assert "DB__PORT" in renamed
    assert "APP__SECRET_KEY" in renamed


def test_flatten_plain_key_not_renamed(sample_env):
    result = flatten_env(sample_env)
    plain = next(e for e in result.entries if e.original_key == "PLAIN_KEY")
    assert not plain.was_renamed


def test_flatten_renamed_count(sample_env):
    result = flatten_env(sample_env)
    assert result.renamed_count == 3


def test_flatten_has_changes_true(sample_env):
    result = flatten_env(sample_env)
    assert result.has_changes is True


def test_flatten_no_changes_when_plain_only():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = flatten_env(env)
    assert not result.has_changes
    assert result.renamed_count == 0


def test_flatten_flat_env_keys(sample_env):
    result = flatten_env(sample_env)
    flat = result.flat_env
    assert "DB_HOST" in flat
    assert "DB_PORT" in flat
    assert "APP_SECRET_KEY" in flat
    assert "PLAIN_KEY" in flat


def test_flatten_flat_env_values_preserved(sample_env):
    result = flatten_env(sample_env)
    assert result.flat_env["DB_HOST"] == "localhost"
    assert result.flat_env["DB_PORT"] == "5432"


def test_flatten_groups_detected(sample_env):
    result = flatten_env(sample_env)
    assert "DB" in result.groups
    assert "APP" in result.groups


def test_flatten_strip_prefix(sample_env):
    result = flatten_env(sample_env, strip_prefix="DB")
    flat = result.flat_env
    # DB__HOST  →  strip DB  →  HOST
    assert "HOST" in flat
    assert "PORT" in flat


def test_flatten_custom_delimiter():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432"}
    result = flatten_env(env, delimiter=".")
    assert result.renamed_count == 2
    assert "DB_HOST" in result.flat_env


# ---------------------------------------------------------------------------
# flatten_formatter
# ---------------------------------------------------------------------------

def test_format_includes_header(sample_env):
    result = flatten_env(sample_env)
    output = format_flatten(result)
    assert "Flatten Report" in output


def test_format_shows_renamed_count(sample_env):
    result = flatten_env(sample_env)
    output = format_flatten(result)
    assert "3" in output


def test_format_shows_groups(sample_env):
    result = flatten_env(sample_env)
    output = format_flatten(result)
    assert "DB" in output
    assert "APP" in output


def test_format_no_changes_message():
    env = {"HOST": "localhost"}
    result = flatten_env(env)
    output = format_flatten(result)
    assert "No keys required flattening" in output
