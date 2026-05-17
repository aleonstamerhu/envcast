"""Score an environment dict for quality/completeness against a set of heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "api_key", "apikey", "private")


@dataclass
class ScoreEntry:
    key: str
    value: str
    deductions: List[Tuple[str, int]] = field(default_factory=list)

    @property
    def score(self) -> int:
        return max(0, 100 - sum(pts for _, pts in self.deductions))


@dataclass
class ScoreResult:
    entries: List[ScoreEntry] = field(default_factory=list)

    @property
    def overall(self) -> int:
        if not self.entries:
            return 100
        return round(sum(e.score for e in self.entries) / len(self.entries))

    @property
    def perfect_count(self) -> int:
        return sum(1 for e in self.entries if e.score == 100)

    @property
    def flagged_count(self) -> int:
        return sum(1 for e in self.entries if e.score < 100)

    def is_healthy(self, threshold: int = 80) -> bool:
        return self.overall >= threshold


def _deductions_for(key: str, value: str) -> List[Tuple[str, int]]:
    issues: List[Tuple[str, int]] = []

    if not value or not value.strip():
        issues.append(("empty value", 30))

    if key != key.upper():
        issues.append(("key not uppercase", 10))

    if " " in key:
        issues.append(("key contains spaces", 20))

    lower_key = key.lower()
    if any(frag in lower_key for frag in _SENSITIVE_FRAGMENTS):
        if value and len(value) < 8:
            issues.append(("sensitive key has short value", 25))

    if value and value.startswith(" "):
        issues.append(("value has leading whitespace", 5))

    if value and value.endswith(" "):
        issues.append(("value has trailing whitespace", 5))

    return issues


def score_env(env: Dict[str, str]) -> ScoreResult:
    """Evaluate each key-value pair and return a ScoreResult."""
    entries: List[ScoreEntry] = []
    for key, value in env.items():
        deductions = _deductions_for(key, value)
        entries.append(ScoreEntry(key=key, value=value, deductions=deductions))
    return ScoreResult(entries=entries)
