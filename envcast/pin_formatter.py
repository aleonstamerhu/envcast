"""envcast.pin_formatter — Human-readable output for PinResult."""
from __future__ import annotations

from typing import Optional
from .pinner import PinResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_pin(result: PinResult, *, color: bool = True) -> str:
    """Return a formatted string describing pin drift in *result*."""
    lines: list[str] = []

    header = "Pinned Environment Report"
    lines.append(_c(header, "1;36") if color else header)
    source_label = result.source or "<unknown>"
    lines.append(f"Source : {source_label}")
    lines.append(
        f"Keys   : {len(result.entries)}  "
        f"Drifted: {result.changed_count}"
    )
    lines.append("")

    if not result.entries:
        lines.append("  (no keys)")
        return "\n".join(lines)

    for entry in result.entries:
        if entry.changed:
            label = _c("~ DRIFT", "1;33") if color else "~ DRIFT"
            lines.append(
                f"  {label}  {entry.key}"
            )
            lines.append(
                f"          pinned : {entry.pinned_value}"
            )
            lines.append(
                f"          current: {entry.value}"
            )
        else:
            label = _c("= OK   ", "32") if color else "= OK   "
            lines.append(f"  {label}  {entry.key}")

    lines.append("")
    if result.has_drift:
        summary = _c(
            f"[!] {result.changed_count} key(s) have drifted from the lockfile.",
            "1;31",
        ) if color else f"[!] {result.changed_count} key(s) have drifted from the lockfile."
    else:
        summary = _c("[✓] All keys match the lockfile.", "1;32") if color else "[✓] All keys match the lockfile."
    lines.append(summary)

    return "\n".join(lines)
