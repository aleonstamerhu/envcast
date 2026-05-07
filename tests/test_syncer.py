"""Tests for envcast.syncer."""

import pytest
from pathlib import Path

from envcast.syncer import sync_env, _write_env_file, SyncResult


@pytest.fixture
def source_env():
    return {"APP_NAME": "envcast", "DEBUG": "true", "NEW_KEY": "hello"}


@pytest.fixture
def target_env():
    return {"APP_NAME": "legacy", "DEBUG": "true", "OLD_KEY": "bye"}


def test_sync_adds_missing_keys(source_env, target_env):
    result = sync_env(source_env, target_env, "fake.env", dry_run=True)
    assert "NEW_KEY" in result.added


def test_sync_updates_changed_keys(source_env, target_env):
    result = sync_env(source_env, target_env, "fake.env", dry_run=True, overwrite=True)
    assert "APP_NAME" in result.updated


def test_sync_skips_changed_when_no_overwrite(source_env, target_env):
    result = sync_env(source_env, target_env, "fake.env", dry_run=True, overwrite=False)
    assert "APP_NAME" in result.skipped
    assert "APP_NAME" not in result.updated


def test_sync_only_missing_skips_changed(source_env, target_env):
    result = sync_env(
        source_env, target_env, "fake.env", dry_run=True, only_missing=True
    )
    assert "APP_NAME" in result.skipped
    assert "NEW_KEY" in result.added


def test_sync_changed_count(source_env, target_env):
    result = sync_env(source_env, target_env, "fake.env", dry_run=True, overwrite=True)
    assert result.changed_count == len(result.added) + len(result.updated)


def test_sync_dry_run_does_not_write(source_env, target_env, tmp_path):
    out = tmp_path / "out.env"
    sync_env(source_env, target_env, str(out), dry_run=True)
    assert not out.exists()


def test_sync_writes_file(source_env, target_env, tmp_path):
    out = tmp_path / "out.env"
    sync_env(source_env, target_env, str(out), dry_run=False, overwrite=True)
    assert out.exists()
    content = out.read_text()
    assert 'NEW_KEY="hello"' in content


def test_write_env_file_sorted(tmp_path):
    out = tmp_path / "sorted.env"
    _write_env_file(str(out), {"Z_KEY": "z", "A_KEY": "a"})
    lines = out.read_text().splitlines()
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("Z_KEY")


def test_sync_unchanged_keys_not_in_added_or_updated(source_env, target_env):
    """Keys present in both source and target with the same value should not
    appear in added or updated regardless of the overwrite flag."""
    result = sync_env(source_env, target_env, "fake.env", dry_run=True, overwrite=True)
    # DEBUG exists in both envs with the same value "true"
    assert "DEBUG" not in result.added
    assert "DEBUG" not in result.updated
