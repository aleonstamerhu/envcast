"""Detect and remove duplicate values across environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateEntry:
    value: str
    keys: List[str]

    @property
    def key_count(self) -> int:
        return len(self.keys)


@dataclass
class DeduplicateResult:
    entries: List[DuplicateEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    strategy: str = "keep_first"

    @property
    def duplicate_count(self) -> int:
        return sum(1 for e in self.entries if e.key_count > 1)

    @property
    def has_duplicates(self) -> bool:
        return self.duplicate_count > 0

    @property
    def removed_keys(self) -> List[str]:
        removed: List[str] = []
        for e in self.entries:
            if e.key_count > 1:
                kept = e.keys[0] if self.strategy == "keep_first" else e.keys[-1]
                removed.extend(k for k in e.keys if k != kept)
        return removed


def deduplicate_env(
    env: Dict[str, str],
    strategy: str = "keep_first",
) -> DeduplicateResult:
    """Group keys that share the same value and optionally collapse them.

    Args:
        env: Source environment mapping.
        strategy: ``keep_first`` retains the alphabetically-first key;
                  ``keep_last`` retains the alphabetically-last key;
                  ``report_only`` leaves *env* unchanged.

    Returns:
        :class:`DeduplicateResult` with duplicate groups and the cleaned env.
    """
    if strategy not in {"keep_first", "keep_last", "report_only"}:
        raise ValueError(f"Unknown strategy: {strategy!r}")

    value_to_keys: Dict[str, List[str]] = {}
    for key in sorted(env):
        value_to_keys.setdefault(env[key], []).append(key)

    entries = [
        DuplicateEntry(value=val, keys=keys)
        for val, keys in value_to_keys.items()
    ]

    if strategy == "report_only":
        cleaned = dict(env)
    else:
        cleaned: Dict[str, str] = {}
        for entry in entries:
            if entry.key_count == 1:
                cleaned[entry.keys[0]] = entry.value
            else:
                kept = entry.keys[0] if strategy == "keep_first" else entry.keys[-1]
                cleaned[kept] = entry.value

    return DeduplicateResult(entries=entries, env=cleaned, strategy=strategy)
