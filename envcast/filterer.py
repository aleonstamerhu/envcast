"""Filter environment variables by pattern, prefix, or predicate."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class FilterEntry:
    key: str
    value: str
    matched: bool
    reason: str  # 'prefix', 'pattern', 'regex', 'predicate', 'none'


@dataclass
class FilterResult:
    entries: List[FilterEntry] = field(default_factory=list)
    mode: str = "include"  # 'include' | 'exclude'

    @property
    def matched_count(self) -> int:
        return sum(1 for e in self.entries if e.matched)

    @property
    def unmatched_count(self) -> int:
        return sum(1 for e in self.entries if not e.matched)

    @property
    def has_matches(self) -> bool:
        return self.matched_count > 0

    def filtered_env(self) -> Dict[str, str]:
        """Return only the keys that survive the filter (respects mode)."""
        if self.mode == "include":
            return {e.key: e.value for e in self.entries if e.matched}
        # exclude mode: keep keys that did NOT match
        return {e.key: e.value for e in self.entries if not e.matched}


def filter_env(
    env: Dict[str, str],
    *,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    regex: Optional[str] = None,
    predicate: Optional[Callable[[str, str], bool]] = None,
    mode: str = "include",
) -> FilterResult:
    """Filter *env* by one or more criteria.

    Only one criterion is applied (checked in order: prefix, pattern,
    regex, predicate).  *mode* controls whether matched keys are kept
    ('include') or removed ('exclude').
    """
    if mode not in ("include", "exclude"):
        raise ValueError(f"mode must be 'include' or 'exclude', got {mode!r}")

    compiled: Optional[re.Pattern] = re.compile(regex) if regex else None
    entries: List[FilterEntry] = []

    for key, value in env.items():
        if prefix is not None:
            matched = key.startswith(prefix)
            reason = "prefix"
        elif pattern is not None:
            matched = fnmatch.fnmatch(key, pattern)
            reason = "pattern"
        elif compiled is not None:
            matched = bool(compiled.search(key))
            reason = "regex"
        elif predicate is not None:
            matched = predicate(key, value)
            reason = "predicate"
        else:
            matched = False
            reason = "none"

        entries.append(FilterEntry(key=key, value=value, matched=matched, reason=reason))

    return FilterResult(entries=entries, mode=mode)
