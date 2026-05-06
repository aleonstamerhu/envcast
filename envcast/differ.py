"""Diff engine for comparing environment variable sets across targets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two environment variable sets."""

    only_in_source: Dict[str, str] = field(default_factory=dict)
    only_in_target: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (source_val, target_val)
    matching: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target or self.changed)

    @property
    def all_keys(self) -> Set[str]:
        return (
            set(self.only_in_source)
            | set(self.only_in_target)
            | set(self.changed)
            | set(self.matching)
        )


def diff_envs(
    source: Dict[str, str],
    target: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two environment variable dictionaries and return a DiffResult.

    Args:
        source: The reference environment (e.g., production).
        target: The environment to compare against.
        ignore_keys: Optional list of keys to exclude from comparison.

    Returns:
        A DiffResult describing the differences.
    """
    ignore = set(ignore_keys or [])
    result = DiffResult()

    all_keys = (set(source) | set(target)) - ignore

    for key in all_keys:
        in_source = key in source
        in_target = key in target

        if in_source and not in_target:
            result.only_in_source[key] = source[key]
        elif in_target and not in_source:
            result.only_in_target[key] = target[key]
        elif source[key] != target[key]:
            result.changed[key] = (source[key], target[key])
        else:
            result.matching[key] = source[key]

    return result
