"""Format an InterpolateResult for terminal output."""
from __future__ import annotations

from typing import List

from .interpolator import InterpolateResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_interpolate(result: InterpolateResult, *, color: bool = True) -> str:
    lines: List[str] = []

    header = "Interpolation Report"
    lines.append(_c(1, header) if color else header)
    lines.append("-" * len(header))
    lines.append(("  " + result.summary))
    lines.append("")

    if result.cycle_keys:
        label = _c(31, "CYCLE") if color else "CYCLE"
        lines.append(f"  Cyclic references ({len(result.cycle_keys)}):")
        for k in sorted(result.cycle_keys):
            lines.append(f"    {label}  {k}")
        lines.append("")

    if result.unresolved_keys:
        label = _c(33, "UNRESOLVED") if color else "UNRESOLVED"
        lines.append(f"  Unresolved references ({len(result.unresolved_keys)}):")
        for k in sorted(result.unresolved_keys):
            lines.append(f"    {label}  {k}")
        lines.append("")

    if result.is_clean:
        ok = _c(32, "OK") if color else "OK"
        lines.append(f"  {ok}  All references resolved successfully.")
        lines.append("")

    return "\n".join(lines)
