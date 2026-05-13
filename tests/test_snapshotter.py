"""Tests for envcast.snapshotter."""
import json
import os
import pytest

from envcast.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


@pytest.fixture()
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


@pytest.fixture()
def updated_env():
    return {"DB_HOST": "prod.db", "DB_PORT": "5432", "NEW_FLAG": "true"}


def test_take_snapshot_stores_env(base_env):
    snap = take_snapshot(base_env, label="test")
    assert snap.env == base_env
    assert snap.label == "test"
    assert snap.captured_at  # non-empty ISO timestamp


def test_take_snapshot_source_optional(base_env):
    snap = take_snapshot(base_env, label="no-src")
    assert snap.source is None


def test_take_snapshot_with_source(base_env):
    snap = take_snapshot(base_env, label="prod", source=".env.prod")
    assert snap.source == ".env.prod"


def test_snapshot_to_dict_round_trip(base_env):
    snap = take_snapshot(base_env, label="rt", source="file.env")
    data = snap.to_dict()
    restored = Snapshot.from_dict(data)
    assert restored.label == snap.label
    assert restored.env == snap.env
    assert restored.source == snap.source
    assert restored.captured_at == snap.captured_at


def test_save_and_load_snapshot(tmp_path, base_env):
    path = str(tmp_path / "snap.json")
    snap = take_snapshot(base_env, label="saved")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded.env == base_env
    assert loaded.label == "saved"


def test_save_snapshot_creates_valid_json(tmp_path, base_env):
    path = str(tmp_path / "snap.json")
    snap = take_snapshot(base_env, label="json-check")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert "env" in data
    assert "captured_at" in data


def test_diff_snapshots_detects_added(base_env, updated_env):
    before = take_snapshot(base_env, label="before")
    after = take_snapshot(updated_env, label="after")
    result = diff_snapshots(before, after)
    assert "NEW_FLAG" in result.added
    assert result.added["NEW_FLAG"] == "true"


def test_diff_snapshots_detects_removed(base_env, updated_env):
    before = take_snapshot(base_env, label="before")
    after = take_snapshot(updated_env, label="after")
    result = diff_snapshots(before, after)
    assert "API_KEY" in result.removed


def test_diff_snapshots_detects_changed(base_env, updated_env):
    before = take_snapshot(base_env, label="before")
    after = take_snapshot(updated_env, label="after")
    result = diff_snapshots(before, after)
    assert "DB_HOST" in result.changed
    assert result.changed["DB_HOST"] == ("localhost", "prod.db")


def test_diff_snapshots_unchanged_key_not_reported(base_env, updated_env):
    before = take_snapshot(base_env, label="before")
    after = take_snapshot(updated_env, label="after")
    result = diff_snapshots(before, after)
    assert "DB_PORT" not in result.added
    assert "DB_PORT" not in result.removed
    assert "DB_PORT" not in result.changed


def test_diff_snapshots_no_changes():
    env = {"KEY": "val"}
    before = take_snapshot(env, label="a")
    after = take_snapshot(env, label="b")
    result = diff_snapshots(before, after)
    assert not result.has_changes


def test_diff_snapshots_has_changes(base_env, updated_env):
    before = take_snapshot(base_env, label="before")
    after = take_snapshot(updated_env, label="after")
    result = diff_snapshots(before, after)
    assert result.has_changes
