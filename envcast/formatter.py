"""Formatters for rendering DiffResult output to the console or string."""

from typing import Optional

from envcast.differ import DiffResult

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_diff(
    result: DiffResult,
    source_label: str = "source",
    target_label: str = "target",
    show_matching: bool = False,
    use_color: bool = True,
    mask_values: bool = False,
) -> str:
    """Render a DiffResult as a human-readable string.

    Args:
        result: The DiffResult to format.
        source_label: Label for the source environment.
        target_label: Label for the target environment.
        show_matching: Whether to include keys that are identical.
        use_color: Whether to include ANSI color codes.
        mask_values: Whether to hide variable values.

    Returns:
        Formatted string representation of the diff.
    """
    lines = []
    header = f"Diff: {source_label} → {target_label}"
    lines.append(_colorize(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for key in sorted(result.only_in_source):
        lines.append(_colorize(f"- {key}={_val(result.only_in_source[key])}", ANSI_RED, use_color))

    for key in sorted(result.only_in_target):
        lines.append(_colorize(f"+ {key}={_val(result.only_in_target[key])}", ANSI_GREEN, use_color))

    for key in sorted(result.changed):
        src_val, tgt_val = result.changed[key]
        lines.append(_colorize(f"~ {key}: {_val(src_val)} → {_val(tgt_val)}", ANSI_YELLOW, use_color))

    if show_matching:
        for key in sorted(result.matching):
            lines.append(f"  {key}={_val(result.matching[key])}")

    if not result.has_differences:
        lines.append(_colorize("No differences found.", ANSI_GREEN, use_color))

    return "\n".join(lines)
