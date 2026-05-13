"""Format SortResult for terminal output."""

from __future__ import annotations

from typing import List

from envcast.sorter import SortResult


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code*."""
    return f"\033[{code}m{text}\033[0m"


def format_sort(result: SortResult, *, show_unchanged: bool = False) -> str:
    """Return a human-readable string describing the sort operation."""
    lines: List[str] = []

    header = _c(f"Sort  [{result.strategy}]  {result.key_count} keys", "1;36")
    lines.append(header)
    lines.append("")  # blank separator

    if not result.order_changed:
        lines.append(_c("  ✔  Already in sorted order — no changes.", "32"))
        return "\n".join(lines)

    lines.append(_c("  Sorted order:", "1"))
    for idx, key in enumerate(result.sorted_order, start=1):
        orig_idx = result.original_order.index(key) + 1
        moved = orig_idx != idx
        marker = _c("↕", "33") if moved else " "
        lines.append(f"  {marker} {key}")

    lines.append("")
    changed = sum(
        1
        for i, k in enumerate(result.sorted_order)
        if result.original_order.index(k) != i
    )
    lines.append(
        _c(f"  {changed} key(s) moved from their original position.", "36")
    )

    return "\n".join(lines)
