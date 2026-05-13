"""Format a CompareResult for terminal output."""

from envcast.comparator import CompareResult

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{_RESET}"


def format_compare(result: CompareResult, no_color: bool = False) -> str:
    def c(color: str, text: str) -> str:
        return text if no_color else _c(color, text)

    lines = [
        c(_BOLD, f"Snapshot comparison: {result.source_label} → {result.target_label}"),
        "",
    ]

    if not result.has_differences:
        lines.append(c(_GREEN, "  ✔ Snapshots are identical."))
        lines.append("")
        return "\n".join(lines)

    for entry in result.removed:
        lines.append(c(_RED, f"  - {entry.key}") + f"  ({entry.source_value!r} → missing)")

    for entry in result.added:
        lines.append(c(_GREEN, f"  + {entry.key}") + f"  (missing → {entry.target_value!r})")

    for entry in result.changed:
        lines.append(
            c(_YELLOW, f"  ~ {entry.key}")
            + f"  ({entry.source_value!r} → {entry.target_value!r})"
        )

    lines.append("")
    summary_parts = []
    if result.added:
        summary_parts.append(c(_GREEN, f"+{len(result.added)} added"))
    if result.removed:
        summary_parts.append(c(_RED, f"-{len(result.removed)} removed"))
    if result.changed:
        summary_parts.append(c(_YELLOW, f"~{len(result.changed)} changed"))
    lines.append("  " + "  ".join(summary_parts))
    lines.append("")

    return "\n".join(lines)
