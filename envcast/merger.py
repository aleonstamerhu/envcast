"""Merge multiple environment sources into a single resolved env dict."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeResult:
    """Outcome of merging two or more environment sources."""

    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    # key -> list of (source_label, value) pairs that were overridden
    sources_used: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)


def merge_envs(
    sources: List[Tuple[str, Dict[str, str]]],
    strategy: str = "last-wins",
) -> MergeResult:
    """Merge a sequence of labelled env dicts.

    Parameters
    ----------
    sources:
        Ordered list of ``(label, env_dict)`` pairs.  Earlier entries have
        lower priority when *strategy* is ``"last-wins"`` (the default).
    strategy:
        ``"last-wins"``  – later sources overwrite earlier ones (default).
        ``"first-wins"`` – earlier sources are preserved; later values are
                           recorded as conflicts but not applied.

    Returns
    -------
    MergeResult
    """
    if strategy not in ("last-wins", "first-wins"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = {}
    conflicts: Dict[str, List[Tuple[str, str]]] = {}
    labels: List[str] = [label for label, _ in sources]

    for label, env in sources:
        for key, value in env.items():
            if key not in merged:
                merged[key] = value
            else:
                existing_value = merged[key]
                if existing_value != value:
                    # Record the conflict regardless of strategy
                    conflicts.setdefault(key, [])
                    if not conflicts[key]:
                        # Include the first occurrence that set the value
                        first_label = _find_first_setter(key, label, sources)
                        conflicts[key].append((first_label, existing_value))
                    conflicts[key].append((label, value))

                    if strategy == "last-wins":
                        merged[key] = value
                # else: same value — no conflict, nothing to do

    return MergeResult(merged=merged, conflicts=conflicts, sources_used=labels)


def _find_first_setter(
    key: str,
    current_label: str,
    sources: List[Tuple[str, Dict[str, str]]],
) -> str:
    """Return the label of the first source that defined *key*."""
    for label, env in sources:
        if label == current_label:
            break
        if key in env:
            return label
    return current_label
