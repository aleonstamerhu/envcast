"""Scope filtering — restrict an env dict to a named prefix or set of prefixes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeEntry:
    key: str
    value: str
    scope: Optional[str]  # matched prefix, or None when unscoped


@dataclass
class ScopeResult:
    entries: List[ScopeEntry] = field(default_factory=list)
    scopes_requested: List[str] = field(default_factory=list)

    # --- convenience properties ---

    def matched_count(self) -> int:
        return sum(1 for e in self.entries if e.scope is not None)

    def unmatched_count(self) -> int:
        return sum(1 for e in self.entries if e.scope is None)

    def has_matches(self) -> bool:
        return self.matched_count() > 0

    def scoped_env(self) -> Dict[str, str]:
        """Return only the matched keys, optionally stripped of their prefix."""
        return {e.key: e.value for e in self.entries if e.scope is not None}

    def stripped_env(self) -> Dict[str, str]:
        """Return matched keys with the leading prefix (and separator) removed."""
        result: Dict[str, str] = {}
        for e in self.entries:
            if e.scope is not None:
                sep = "_"
                stripped = e.key[len(e.scope) + len(sep):] if e.key.startswith(e.scope + sep) else e.key
                result[stripped] = e.value
        return result


def scope_env(
    env: Dict[str, str],
    prefixes: List[str],
    *,
    case_sensitive: bool = False,
) -> ScopeResult:
    """Filter *env* to keys that start with any of the given *prefixes*.

    Parameters
    ----------
    env:
        Source environment mapping.
    prefixes:
        List of prefix strings (e.g. ``["DB", "AWS"]``).
    case_sensitive:
        When *False* (default) comparisons are case-insensitive.
    """
    normalised = [
        p if case_sensitive else p.upper()
        for p in prefixes
    ]

    entries: List[ScopeEntry] = []
    for key, value in env.items():
        cmp_key = key if case_sensitive else key.upper()
        matched_prefix: Optional[str] = None
        for orig, norm in zip(prefixes, normalised):
            if cmp_key == norm or cmp_key.startswith(norm + "_"):
                matched_prefix = orig
                break
        entries.append(ScopeEntry(key=key, value=value, scope=matched_prefix))

    return ScopeResult(entries=entries, scopes_requested=list(prefixes))
