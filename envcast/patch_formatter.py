"""Human-readable formatter for :class:`~envcast.patcher.PatchResult`."""
from __future__ import annotations

from typing import Optional

from envcast.patcher import PatchResult

_RESET  = "\033[0m"
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_YELLOW = "\033[33m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"


def _c(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


def format_patch(result: PatchResult, *, color: bool = True) -> str:
    """Return a formatted string describing every entry in *result*."""
    lines: list[str] = []

    header = f"Patch summary — {result.set_count} set, {result.unset_count} unset"
    lines.append(_c(header, _BOLD) if color else header)
    lines.append("")

    if not result.entries:
        lines.append("  (nothing to patch)")
        return "\n".join(lines)

    for entry in result.entries:
        if entry.action == "set":
            if entry.old_value is None:
                label = _c("+ ADD", _GREEN, _BOLD) if color else "+ ADD"
                detail = f"{entry.key} = {entry.new_value!r}"
            else:
                label = _c("~ UPD", _YELLOW, _BOLD) if color else "~ UPD"
                detail = (
                    f"{entry.key}: {entry.old_value!r} → {entry.new_value!r}"
                )
            lines.append(f"  {label}  {detail}")

        elif entry.action == "unset":
            label = _c("- DEL", _RED, _BOLD) if color else "- DEL"
            lines.append(f"  {label}  {entry.key} (was {entry.old_value!r})")

        else:  # noop
            label = _c("  ---", _DIM) if color else "  ---"
            lines.append(f"  {label}  {entry.key} (no change)")

    return "\n".join(lines)
