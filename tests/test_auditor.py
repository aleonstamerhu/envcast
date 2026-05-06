"""Tests for envcast.auditor."""

import json
import os
import pytest
from dataclasses import dataclass, field
from typing import List

from envcast.auditor import (
    AuditEntry,
    AuditLog,
    record_diff,
    record_sync,
    save_audit_log,
    load_audit_log,
)


# ---------------------------------------------------------------------------
# Minimal stubs that mimic DiffResult / SyncResult public attributes
# ---------------------------------------------------------------------------

@dataclass
class _FakeDiff:
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    changed: dict = field(default_factory=dict)
    matching: List[str] = field(default_factory=list)
    has_differences: bool = False


@dataclass
class _FakeSync:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    changed_count: int = 0


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def diff_result():
    return _FakeDiff(
        only_in_source=["REMOVED"],
        only_in_target=["ADDED"],
        changed={"KEY": ("old", "new")},
        matching=["SAME"],
        has_differences=True,
    )


@pytest.fixture
def sync_result():
    return _FakeSync(
        added=["ADDED"],
        updated=["KEY"],
        skipped=[],
        unchanged=["SAME"],
        changed_count=2,
    )


# ---------------------------------------------------------------------------
# record_diff
# ---------------------------------------------------------------------------

def test_record_diff_operation(diff_result):
    entry = record_diff("source.env", "target.env", diff_result)
    assert entry.operation == "diff"


def test_record_diff_paths(diff_result):
    entry = record_diff("source.env", "target.env", diff_result)
    assert entry.source == "source.env"
    assert entry.target == "target.env"


def test_record_diff_summary_keys(diff_result):
    entry = record_diff("source.env", "target.env", diff_result)
    assert "only_in_source" in entry.summary
    assert "only_in_target" in entry.summary
    assert "changed" in entry.summary
    assert "has_differences" in entry.summary
    assert entry.summary["has_differences"] is True


def test_record_diff_timestamp_is_string(diff_result):
    entry = record_diff("s", "t", diff_result)
    assert isinstance(entry.timestamp, str) and len(entry.timestamp) > 0


# ---------------------------------------------------------------------------
# record_sync
# ---------------------------------------------------------------------------

def test_record_sync_operation(sync_result):
    entry = record_sync("source.env", "target.env", sync_result)
    assert entry.operation == "sync"


def test_record_sync_summary_changed_count(sync_result):
    entry = record_sync("source.env", "target.env", sync_result)
    assert entry.summary["changed_count"] == 2


def test_record_sync_summary_lists(sync_result):
    entry = record_sync("source.env", "target.env", sync_result)
    assert "ADDED" in entry.summary["added"]
    assert "KEY" in entry.summary["updated"]


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

def test_audit_log_len(diff_result, sync_result):
    log = AuditLog()
    log.add(record_diff("s", "t", diff_result))
    log.add(record_sync("s", "t", sync_result))
    assert len(log) == 2


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_audit_log(tmp_path, diff_result, sync_result):
    log_path = str(tmp_path / "audit.jsonl")
    log = AuditLog()
    log.add(record_diff("source.env", "target.env", diff_result))
    log.add(record_sync("source.env", "target.env", sync_result))

    save_audit_log(log, log_path)

    loaded = load_audit_log(log_path)
    assert len(loaded) == 2
    assert loaded.entries[0].operation == "diff"
    assert loaded.entries[1].operation == "sync"


def test_save_appends_to_existing(tmp_path, diff_result):
    log_path = str(tmp_path / "audit.jsonl")
    for _ in range(3):
        log = AuditLog()
        log.add(record_diff("s", "t", diff_result))
        save_audit_log(log, log_path)

    loaded = load_audit_log(log_path)
    assert len(loaded) == 3


def test_saved_file_is_valid_jsonl(tmp_path, sync_result):
    log_path = str(tmp_path / "audit.jsonl")
    log = AuditLog()
    log.add(record_sync("s", "t", sync_result))
    save_audit_log(log, log_path)

    with open(log_path) as fh:
        lines = [l.strip() for l in fh if l.strip()]
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["operation"] == "sync"
