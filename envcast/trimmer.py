"""trimmer.py – strip leading/trailing whitespace from env var values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimEntry:
    key: str
    original: str
    trimmed: str

    @property
    def was_trimmed(self) -> bool:
        return self.original != self.trimmed


@dataclass
class TrimResult:
    entries: List[TrimEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def trimmed_count(self) -> int:
        return sum(1 for e in self.entries if e.was_trimmed)

    @property
    def has_changes(self) -> bool:
        return self.trimmed_count > 0

    @property
    def clean_count(self) -> int:
        return len(self.entries) - self.trimmed_count


def trim_env(env: Dict[str, str]) -> TrimResult:
    """Return a TrimResult with whitespace stripped from every value."""
    entries: List[TrimEntry] = []
    trimmed_env: Dict[str, str] = {}

    for key, value in env.items():
        trimmed_value = value.strip()
        entries.append(TrimEntry(key=key, original=value, trimmed=trimmed_value))
        trimmed_env[key] = trimmed_value

    return TrimResult(entries=entries, env=trimmed_env)
