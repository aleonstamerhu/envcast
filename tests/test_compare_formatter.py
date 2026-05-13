"""Tests for envcast.compare_formatter."""

import pytest
from envcast.snapshotter import Snapshot
from envcast.comparator import compare_snapshots_report
from envcast.compare_formatter import format_compare


@pytest.fixture
def diff_result():
    snap_a = Snapshot(env={"DB_HOST": "localhost", "PORT": "5432"}, source="staging")
    snap_b = Snapshot(env={"DB_HOST": "prod.db", "API_KEY": "abc"}, source="production")
    return compare_snapshots_report(snap_a, snap_b)


@pytest.fixture
def identical_result():
    snap = Snapshot(env={"X": "1"}, source="a")
    snap2 = Snapshot(env={"X": "1"}, source="b")
    return compare_snapshots_report(snap, snap2)


def test_format_includes_header(diff_result):
    output = format_compare(diff_result, no_color=True)
    assert "staging" in output
    assert "production" in output


def test_format_shows_removed_key(diff_result):
    output = format_compare(diff_result, no_color=True)
    assert "PORT" in output
    assert "missing" in output


def test_format_shows_added_key(diff_result):
    output = format_compare(diff_result, no_color=True)
    assert "API_KEY" in output


def test_format_shows_changed_key(diff_result):
    output = format_compare(diff_result, no_color=True)
    assert "DB_HOST" in output
    assert "localhost" in output
    assert "prod.db" in output


def test_format_identical_shows_no_differences(identical_result):
    output = format_compare(identical_result, no_color=True)
    assert "identical" in output.lower()


def test_format_summary_counts_present(diff_result):
    output = format_compare(diff_result, no_color=True)
    assert "+1" in output or "added" in output
    assert "-1" in output or "removed" in output
    assert "~1" in output or "changed" in output


def test_format_with_color_does_not_crash(diff_result):
    output = format_compare(diff_result, no_color=False)
    assert "DB_HOST" in output
