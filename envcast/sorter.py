"""Sort environment variable keys with optional grouping strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    """Result of sorting an environment variable mapping."""

    sorted_env: Dict[str, str]
    original_order: List[str]
    sorted_order: List[str]
    strategy: str

    @property
    def order_changed(self) -> bool:
        return self.original_order != self.sorted_order

    @property
    def key_count(self) -> int:
        return len(self.sorted_order)


def sort_env(
    env: Dict[str, str],
    strategy: str = "alpha",
    groups: Optional[List[str]] = None,
) -> SortResult:
    """Sort *env* keys according to *strategy*.

    Strategies
    ----------
    alpha       : simple A-Z case-insensitive sort (default)
    alpha_desc  : Z-A case-insensitive sort
    length      : shortest key first
    grouped     : prefix groups first (requires *groups* list), then alpha
    """
    original_order = list(env.keys())

    if strategy == "alpha":
        sorted_keys = sorted(original_order, key=str.casefold)
    elif strategy == "alpha_desc":
        sorted_keys = sorted(original_order, key=str.casefold, reverse=True)
    elif strategy == "length":
        sorted_keys = sorted(original_order, key=lambda k: (len(k), k.casefold()))
    elif strategy == "grouped":
        sorted_keys = _grouped_sort(original_order, groups or [])
    else:
        raise ValueError(f"Unknown sort strategy: {strategy!r}")

    sorted_env = {k: env[k] for k in sorted_keys}

    return SortResult(
        sorted_env=sorted_env,
        original_order=original_order,
        sorted_order=sorted_keys,
        strategy=strategy,
    )


def _grouped_sort(keys: List[str], groups: List[str]) -> List[str]:
    """Place keys whose names start with a group prefix first, then the rest."""
    grouped: List[str] = []
    remainder: List[str] = []

    for key in sorted(keys, key=str.casefold):
        if any(key.upper().startswith(g.upper()) for g in groups):
            grouped.append(key)
        else:
            remainder.append(key)

    return grouped + remainder
