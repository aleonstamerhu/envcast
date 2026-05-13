"""Format LintResult for terminal output."""
from __future__ import annotations

from typing import List

from envcast.linter import LintResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _c(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


def format_lint(result: LintResult, *, color: bool = True) -> str:
    lines: List[str] = []

    header = "Lint Report"
    lines.append(_c(header, _BOLD) if color else header)
    lines.append("-" * 40)

    if result.is_clean:
        msg = "No issues found."
        lines.append(_c(msg, _CYAN) if color else msg)
    else:
        for issue in result.errors:
            prefix = "[ERROR]  "
            text = f"{prefix}{issue.key}: {issue.message}"
            lines.append(_c(text, _RED) if color else text)

        for issue in result.warnings:
            prefix = "[WARN]   "
            text = f"{prefix}{issue.key}: {issue.message}"
            lines.append(_c(text, _YELLOW) if color else text)

    lines.append("-" * 40)
    summary = (
        f"Summary: {result.error_count} error(s), {result.warning_count} warning(s)"
    )
    lines.append(_c(summary, _BOLD) if color else summary)

    return "\n".join(lines)
