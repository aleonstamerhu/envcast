"""Terminal formatter for RotateResult."""
from __future__ import annotations

from typing import Optional

from .rotator import RotateResult


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code*."""
    return f"\033[{code}m{text}\033[0m"


def format_rotate(result: RotateResult, *, apply: bool = False) -> str:
    lines: list[str] = []

    mode = "applied" if apply else "suggested"
    lines.append(_c(f"=== Key Rotation Report ({mode}) ===", "1"))
    lines.append("")

    suggestions = result.keys_with_suggestions()
    if not suggestions:
        lines.append(_c("  No stale keys detected.", "32"))
    else:
        for entry in suggestions:
            arrow = _c("→", "33")
            old = _c(entry.key, "31")
            new = _c(entry.suggested_key or "", "32")
            status = _c("[rotated]", "32") if entry.rotated else _c("[suggestion]", "33")
            reason = f"  ({entry.reason})" if entry.reason else ""
            lines.append(f"  {old}  {arrow}  {new}  {status}{reason}")

    lines.append("")
    total = len(result.entries)
    rotated = result.rotated_count
    flagged = len(suggestions)
    lines.append(
        _c(
            f"Summary: {total} keys scanned, "
            f"{flagged} flagged, "
            f"{rotated} rotated.",
            "1",
        )
    )
    return "\n".join(lines)
