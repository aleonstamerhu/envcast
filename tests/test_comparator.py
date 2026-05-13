"""Tests for envcast.comparator."""

import pytest
from envcast.snapshotter import Snapshot
from envcast.comparator import compare_snapshots_report, CompareResult


@pytest.fixture
def snap_a():
    return Snapshot(env={"DB_HOST": "localhost", "PORT": "5432", "SHARED": "same"}, source="env-a")


@pytest.fixture
def snap_b():
    return Snapshot(env={"DB_HOST": "prod.db", "API_KEY": "secret", "SHARED": "same"}, source="env-b")


def test_compare_labels(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    assert result.source_label == "env-a"
    assert result.target_label == "env-b"


def test_compare_detects_removed(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    keys = [e.key for e in result.removed]
    assert "PORT" in keys


def test_compare_detects_added(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    keys = [e.key for e in result.added]
    assert "API_KEY" in keys


def test_compare_detects_changed(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    keys = [e.key for e in result.changed]
    assert "DB_HOST" in keys


def test_compare_unchanged_excluded_by_default(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    keys = [e.key for e in result.entries]
    assert "SHARED" not in keys


def test_compare_unchanged_included_when_requested(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b, include_unchanged=True)
    keys = [e.key for e in result.unchanged]
    assert "SHARED" in keys


def test_compare_has_differences(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    assert result.has_differences is True


def test_compare_no_differences_when_identical():
    snap = Snapshot(env={"A": "1", "B": "2"}, source="x")
    snap2 = Snapshot(env={"A": "1", "B": "2"}, source="y")
    result = compare_snapshots_report(snap, snap2)
    assert result.has_differences is False


def test_compare_difference_count(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    # removed: PORT, added: API_KEY, changed: DB_HOST
    assert result.difference_count == 3


def test_compare_entry_values(snap_a, snap_b):
    result = compare_snapshots_report(snap_a, snap_b)
    changed = {e.key: e for e in result.changed}
    assert changed["DB_HOST"].source_value == "localhost"
    assert changed["DB_HOST"].target_value == "prod.db"
