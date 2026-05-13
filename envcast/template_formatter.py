"""Console formatter for TemplateResult."""
from __future__ import annotations

from envcast.templater import TemplateResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_DIM = "\033[2m"


def _c(code: str, text: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_template(result: TemplateResult, color: bool = True) -> str:
    lines = []
    total = len(result.entries)
    req = len(result.required_keys)
    opt = len(result.optional_keys)

    lines.append(
        _c(_BOLD, f"Template Summary: {total} keys ({req} required, {opt} optional)", color)
    )
    lines.append("")

    if result.required_keys:
        lines.append(_c(_CYAN, "Required:", color))
        for key in result.required_keys:
            lines.append(f"  {_c(_BOLD, key, color)}")

    if result.optional_keys:
        lines.append("")
        lines.append(_c(_YELLOW, "Optional:", color))
        for key in result.optional_keys:
            lines.append(f"  {_c(_DIM, key, color)}")

    return "\n".join(lines) + "\n"
