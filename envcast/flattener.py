"""Flatten nested environment variable groups into a single-level dict.

Supports a delimiter-based convention where keys like DB__HOST or DB__PORT
are treated as nested structures and can be flattened back to a simple
key=value mapping with optional prefix stripping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenEntry:
    original_key: str
    flat_key: str
    value: str
    group: Optional[str]  # prefix/group extracted, e.g. "DB"

    @property
    def was_renamed(self) -> bool:
        return self.original_key != self.flat_key


@dataclass
class FlattenResult:
    entries: List[FlattenEntry] = field(default_factory=list)
    delimiter: str = "__"

    @property
    def renamed_count(self) -> int:
        return sum(1 for e in self.entries if e.was_renamed)

    @property
    def has_changes(self) -> bool:
        return self.renamed_count > 0

    @property
    def flat_env(self) -> Dict[str, str]:
        return {e.flat_key: e.value for e in self.entries}

    @property
    def groups(self) -> List[str]:
        seen: List[str] = []
        for e in self.entries:
            if e.group and e.group not in seen:
                seen.append(e.group)
        return seen


def flatten_env(
    env: Dict[str, str],
    delimiter: str = "__",
    strip_prefix: Optional[str] = None,
) -> FlattenResult:
    """Flatten env keys that use *delimiter* as a hierarchy separator.

    Parameters
    ----------
    env:
        Source environment dictionary.
    delimiter:
        Token used to denote nesting levels (default ``__``).
    strip_prefix:
        If provided, remove this prefix (case-insensitive) from every
        flattened key.  E.g. strip_prefix="APP" turns APP__DB__HOST
        into DB__HOST.
    """
    entries: List[FlattenEntry] = []

    for original_key, value in env.items():
        parts = original_key.split(delimiter)
        group: Optional[str] = parts[0] if len(parts) > 1 else None

        if strip_prefix and parts[0].upper() == strip_prefix.upper():
            parts = parts[1:]

        flat_key = "_".join(parts)  # collapse remaining segments with single _

        entries.append(
            FlattenEntry(
                original_key=original_key,
                flat_key=flat_key,
                value=value,
                group=group,
            )
        )

    return FlattenResult(entries=entries, delimiter=delimiter)
