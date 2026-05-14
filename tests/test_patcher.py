"""Tests for envcast.patcher."""
from __future__ import annotations

import pytest

from envcast.patcher import patch_env, PatchResult


@pytest.fixture()
def base_env() -> dict:
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "secret",
    }


# ------------------------------------------------------------------ basic ops

def test_patch_adds_new_key(base_env):
    result = patch_env(base_env, {"NEW_KEY": "value"})
    assert result.env["NEW_KEY"] == "value"


def test_patch_updates_existing_key(base_env):
    result = patch_env(base_env, {"APP_PORT": "9090"})
    assert result.env["APP_PORT"] == "9090"


def test_patch_removes_key_when_value_is_none(base_env):
    result = patch_env(base_env, {"DB_PASSWORD": None})
    assert "DB_PASSWORD" not in result.env


def test_patch_preserves_untouched_keys(base_env):
    result = patch_env(base_env, {"APP_PORT": "9090"})
    assert result.env["APP_HOST"] == "localhost"
    assert result.env["DB_PASSWORD"] == "secret"


# ------------------------------------------------------------------ actions

def test_action_set_for_new_key(base_env):
    result = patch_env(base_env, {"FRESH": "yes"})
    entry = next(e for e in result.entries if e.key == "FRESH")
    assert entry.action == "set"
    assert entry.old_value is None


def test_action_set_for_updated_key(base_env):
    result = patch_env(base_env, {"APP_HOST": "prod.example.com"})
    entry = next(e for e in result.entries if e.key == "APP_HOST")
    assert entry.action == "set"
    assert entry.old_value == "localhost"


def test_action_unset_for_removed_key(base_env):
    result = patch_env(base_env, {"APP_PORT": None})
    entry = next(e for e in result.entries if e.key == "APP_PORT")
    assert entry.action == "unset"


def test_action_noop_when_value_unchanged(base_env):
    result = patch_env(base_env, {"APP_HOST": "localhost"})
    entry = next(e for e in result.entries if e.key == "APP_HOST")
    assert entry.action == "noop"


def test_action_noop_when_unset_missing_key(base_env):
    result = patch_env(base_env, {"GHOST": None})
    entry = next(e for e in result.entries if e.key == "GHOST")
    assert entry.action == "noop"


# ------------------------------------------------------------------ allow_new

def test_allow_new_false_skips_unknown_key(base_env):
    result = patch_env(base_env, {"BRAND_NEW": "hi"}, allow_new=False)
    assert "BRAND_NEW" not in result.env
    entry = next(e for e in result.entries if e.key == "BRAND_NEW")
    assert entry.action == "noop"


def test_allow_new_false_still_updates_existing_key(base_env):
    result = patch_env(base_env, {"APP_PORT": "443"}, allow_new=False)
    assert result.env["APP_PORT"] == "443"


# ------------------------------------------------------------------ counters

def test_set_count(base_env):
    result = patch_env(base_env, {"APP_PORT": "9090", "NEW": "x"})
    assert result.set_count == 2


def test_unset_count(base_env):
    result = patch_env(base_env, {"APP_PORT": None, "DB_PASSWORD": None})
    assert result.unset_count == 2


def test_has_changes_true(base_env):
    result = patch_env(base_env, {"APP_PORT": "9090"})
    assert result.has_changes is True


def test_has_changes_false_when_all_noop(base_env):
    result = patch_env(base_env, {"APP_HOST": "localhost"})
    assert result.has_changes is False


def test_empty_patch_leaves_env_unchanged(base_env):
    result = patch_env(base_env, {})
    assert result.env == base_env
    assert result.changed_count == 0
