"""Tests for envcast.pinner and envcast.pin_formatter."""
import json
import os
import pytest

from envcast.pinner import (
    PinEntry,
    PinResult,
    _checksum,
    load_lockfile,
    write_lockfile,
    pin_env,
)
from envcast.pin_formatter import format_pin


@pytest.fixture
def current_env():
    return {"APP_ENV": "production", "DB_HOST": "db.example.com", "PORT": "8080"}


@pytest.fixture
def locked_env():
    return {"APP_ENV": "production", "DB_HOST": "old.db.example.com", "PORT": "8080"}


# ---------------------------------------------------------------------------
# pin_env
# ---------------------------------------------------------------------------

def test_pin_env_returns_pin_result(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    assert isinstance(result, PinResult)


def test_pin_env_entry_count_matches_current(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    assert len(result.entries) == len(current_env)


def test_pin_env_detects_drift(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    assert result.has_drift
    assert result.changed_count == 1


def test_pin_env_no_drift_when_identical(current_env):
    result = pin_env(current_env, dict(current_env))
    assert not result.has_drift
    assert result.changed_count == 0


def test_pin_env_new_key_not_flagged_as_drift(current_env):
    """A key absent from the lockfile should be pinned to its current value."""
    locked = {k: v for k, v in current_env.items() if k != "PORT"}
    result = pin_env(current_env, locked)
    port_entry = next(e for e in result.entries if e.key == "PORT")
    assert not port_entry.changed
    assert port_entry.pinned_value == current_env["PORT"]


def test_pin_env_pinned_env_reflects_lock(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    assert result.pinned_env["DB_HOST"] == locked_env["DB_HOST"]


def test_pin_env_stores_source(current_env, locked_env):
    result = pin_env(current_env, locked_env, source="staging")
    assert result.source == "staging"


# ---------------------------------------------------------------------------
# lockfile I/O
# ---------------------------------------------------------------------------

def test_write_and_load_lockfile(tmp_path, current_env):
    path = str(tmp_path / "env.lock")
    write_lockfile(path, current_env)
    loaded = load_lockfile(path)
    assert loaded == current_env


def test_load_lockfile_missing_returns_empty(tmp_path):
    path = str(tmp_path / "nonexistent.lock")
    assert load_lockfile(path) == {}


def test_write_lockfile_includes_checksum(tmp_path, current_env):
    path = str(tmp_path / "env.lock")
    write_lockfile(path, current_env)
    with open(path) as fh:
        data = json.load(fh)
    assert "checksum" in data
    assert data["checksum"] == _checksum(current_env)


# ---------------------------------------------------------------------------
# format_pin
# ---------------------------------------------------------------------------

def test_format_includes_header(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    output = format_pin(result, color=False)
    assert "Pinned Environment Report" in output


def test_format_shows_drifted_key(current_env, locked_env):
    result = pin_env(current_env, locked_env)
    output = format_pin(result, color=False)
    assert "DB_HOST" in output
    assert "DRIFT" in output


def test_format_no_drift_shows_ok(current_env):
    result = pin_env(current_env, dict(current_env))
    output = format_pin(result, color=False)
    assert "All keys match the lockfile" in output
