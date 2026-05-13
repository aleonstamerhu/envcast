"""Format a RenameResult for terminal output."""

from typing import List

from .renamer import RenameResult


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code* (reset afterwards)."""
    return f"\033[{code}m{text}\033[0m"


def format_rename(result: RenameResult, *, color: bool = True) -> str:
    """Return a human-readable summary of a :class:`RenameResult`."""
    lines: List[str] = []

    header = "Key Rename Summary"
    lines.append(_c(header, "1;36") if color else header)
    lines.append(
        f"  Renamed : {result.renamed_count}  "
        f"Skipped : {result.skipped_count}"
    )
    lines.append("")

    if result.has_renames:
        section = "Renamed keys:"
        lines.append(_c(section, "1") if color else section)
        for entry in result.entries:
            if not entry.skipped:
                arrow = _c("->", "32") if color else "->"
                lines.append(f"  {entry.old_key}  {arrow}  {entry.new_key}")
        lines.append("")

    if result.skipped_count:
        section = "Skipped (key not found):"
        lines.append(_c(section, "1;33") if color else section)
        for entry in result.entries:
            if entry.skipped:
                label = _c(entry.old_key, "33") if color else entry.old_key
                lines.append(f"  {label}")
        lines.append("")

    return "\n".join(lines)
