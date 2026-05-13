"""Snapshot: capture and compare point-in-time environment state."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class Snapshot:
    label: str
    captured_at: str
    env: Dict[str, str]
    source: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "captured_at": self.captured_at,
            "source": self.source,
            "env": self.env,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            label=data["label"],
            captured_at=data["captured_at"],
            env=data["env"],
            source=data.get("source"),
        )


@dataclass
class SnapshotDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def take_snapshot(env: Dict[str, str], label: str, source: Optional[str] = None) -> Snapshot:
    """Create a snapshot of the given env mapping."""
    return Snapshot(label=label, captured_at=_now_iso(), env=dict(env), source=source)


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return what changed between them."""
    all_keys = set(before.env) | set(after.env)
    result = SnapshotDiff()
    for key in all_keys:
        in_before = key in before.env
        in_after = key in after.env
        if in_before and not in_after:
            result.removed[key] = before.env[key]
        elif in_after and not in_before:
            result.added[key] = after.env[key]
        elif before.env[key] != after.env[key]:
            result.changed[key] = (before.env[key], after.env[key])
    return result
