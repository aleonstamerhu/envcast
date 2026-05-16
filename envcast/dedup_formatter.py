"""Format :class:`~envcast.deduplicator.DeduplicateResult` for terminal output."""
from __future__ import annotations

from typing import List

from envcast.deduplicator import DeduplicateResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_dedup(result: DeduplicateResult, *, color: bool = True) -> str:
    """Return a human-readable report of duplicate value groups."""

    def c(code: str, text: str) -> str:
        return _c(code, text) if color else text

    lines: List[str] = []
    header = c("1;36", f"=== Deduplication Report (strategy: {result.strategy}) ===")
    lines.append(header)

    if not result.has_duplicates:
        lines.append(c("32", "  No duplicate values found."))
        return "\n".join(lines)

    lines.append(
        c("33", f"  {result.duplicate_count} duplicate group(s) detected.")
    )
    lines.append("")

    for entry in result.entries:
        if entry.key_count < 2:
            continue
        kept = (
            entry.keys[0] if result.strategy in {"keep_first", "report_only"}
            else entry.keys[-1]
        )
        lines.append(c("1", f"  Value: {entry.value!r}"))
        for key in entry.keys:
            if result.strategy == "report_only":
                marker = c("33", "~")
            elif key == kept:
                marker = c("32", "+")
            else:
                marker = c("31", "-")
            lines.append(f"    {marker} {key}")
        lines.append("")

    removed = result.removed_keys
    if removed:
        lines.append(
            c("31", f"  Removed {len(removed)} key(s): {', '.join(removed)}")
        )

    return "\n".join(lines)
