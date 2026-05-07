"""Format ProfileResult for terminal output."""

from __future__ import annotations

from typing import List
from envcast.profiler import ProfileResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _c(color: str, text: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_profile(result: ProfileResult, color: bool = True) -> str:
    """Render a ProfileResult as a human-readable string."""
    lines: List[str] = []
    summary = result.summary()

    header = _c(_BOLD, f"Profile Summary ({summary['total']} keys)", color)
    lines.append(header)
    lines.append("-" * 40)

    if result.sensitive_keys:
        label = _c(_RED, "Sensitive keys", color)
        lines.append(f"  {label}: {', '.join(sorted(result.sensitive_keys))}")
    else:
        lines.append("  Sensitive keys: none")

    if result.empty_keys:
        label = _c(_YELLOW, "Empty values", color)
        lines.append(f"  {label}: {', '.join(sorted(result.empty_keys))}")
    else:
        lines.append("  Empty values: none")

    if result.url_keys:
        label = _c(_CYAN, "URL values", color)
        lines.append(f"  {label}: {', '.join(sorted(result.url_keys))}")

    if result.port_keys:
        label = _c(_CYAN, "Port values", color)
        lines.append(f"  {label}: {', '.join(sorted(result.port_keys))}")

    lines.append("-" * 40)
    counts = (
        f"sensitive={summary['sensitive']}  "
        f"empty={summary['empty']}  "
        f"urls={summary['urls']}  "
        f"ports={summary['ports']}"
    )
    lines.append(counts)
    return "\n".join(lines)
