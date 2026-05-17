"""Formatter for FlattenResult — produces a human-readable terminal report."""
from __future__ import annotations

from typing import List

from envcast.flattener import FlattenResult


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour *code*."""
    return f"\033[{code}m{text}\033[0m"


def format_flatten(result: FlattenResult, *, show_unchanged: bool = False) -> str:
    lines: List[str] = []

    title = _c("1;34", "=== Flatten Report ===")
    lines.append(title)

    total = len(result.entries)
    renamed = result.renamed_count
    lines.append(
        f"  Keys processed : {total}"
    )
    lines.append(
        f"  Keys renamed   : {_c('1;33', str(renamed)) if renamed else _c('32', '0')}"
    )

    if result.groups:
        lines.append(f"  Groups found   : {', '.join(_c('36', g) for g in result.groups)}")

    lines.append("")

    for entry in result.entries:
        if not entry.was_renamed and not show_unchanged:
            continue
        old = _c("31", entry.original_key)
        new = _c("32", entry.flat_key)
        lines.append(f"  {old}  →  {new}  =  {entry.value}")

    if not any(e.was_renamed for e in result.entries):
        lines.append(_c("32", "  No keys required flattening."))

    return "\n".join(lines)
