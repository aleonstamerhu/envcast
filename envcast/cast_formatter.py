"""Format a CastResult for terminal output."""
from __future__ import annotations

from typing import Optional

from envcast.caster import CastResult

_COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
}


def _c(text: str, *codes: str, color: bool = True) -> str:
    if not color:
        return text
    prefix = "".join(_COLORS[c] for c in codes)
    return f"{prefix}{text}{_COLORS['reset']}"


_TYPE_COLOR = {
    "bool": "yellow",
    "int": "cyan",
    "float": "cyan",
    "str": "green",
}


def format_cast(result: CastResult, *, color: bool = True, show_unchanged: bool = True) -> str:
    lines: list[str] = []
    lines.append(_c("=== envcast: type cast ===", "bold", color=color))

    for entry in result.entries:
        type_col = _TYPE_COLOR.get(entry.type_label, "green")
        type_label = _c(f"[{entry.type_label}]", type_col, color=color)

        if entry.failed:
            tag = _c("FAIL", "red", "bold", color=color)
            lines.append(f"  {tag} {entry.key}: {entry.raw!r}  ({entry.error})")
        elif entry.type_label == "str" and not show_unchanged:
            continue
        else:
            lines.append(f"  {type_label} {entry.key} = {entry.cast_value!r}")

    total = len(result.entries)
    failed = result.failed_count
    summary = _c(
        f"\n{total} key(s) processed, {failed} failure(s).",
        "bold",
        color=color,
    )
    lines.append(summary)
    return "\n".join(lines)
