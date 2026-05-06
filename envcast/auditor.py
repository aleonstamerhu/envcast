"""Audit log for tracking sync and diff operations performed by envcast."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: str
    operation: str          # 'diff' | 'sync'
    source: str
    target: str
    summary: dict
    user: Optional[str] = None


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _current_user() -> Optional[str]:
    try:
        return os.environ.get("USER") or os.environ.get("USERNAME")
    except Exception:
        return None


def record_diff(source: str, target: str, diff_result) -> AuditEntry:
    """Create an AuditEntry for a diff operation."""
    summary = {
        "only_in_source": list(diff_result.only_in_source),
        "only_in_target": list(diff_result.only_in_target),
        "changed": list(diff_result.changed.keys()),
        "matching": list(diff_result.matching),
        "has_differences": diff_result.has_differences,
    }
    return AuditEntry(
        timestamp=_now_iso(),
        operation="diff",
        source=source,
        target=target,
        summary=summary,
        user=_current_user(),
    )


def record_sync(source: str, target: str, sync_result) -> AuditEntry:
    """Create an AuditEntry for a sync operation."""
    summary = {
        "added": list(sync_result.added),
        "updated": list(sync_result.updated),
        "skipped": list(sync_result.skipped),
        "unchanged": list(sync_result.unchanged),
        "changed_count": sync_result.changed_count,
    }
    return AuditEntry(
        timestamp=_now_iso(),
        operation="sync",
        source=source,
        target=target,
        summary=summary,
        user=_current_user(),
    )


def save_audit_log(log: AuditLog, path: str) -> None:
    """Append entries to a JSON-lines audit log file."""
    with open(path, "a", encoding="utf-8") as fh:
        for entry in log.entries:
            fh.write(json.dumps(asdict(entry)) + "\n")


def load_audit_log(path: str) -> AuditLog:
    """Load all entries from a JSON-lines audit log file."""
    log = AuditLog()
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                data = json.loads(line)
                log.add(AuditEntry(**data))
    return log
