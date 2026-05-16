"""Format NormalizeResult for terminal output."""

from typing import Optional
from envcast.normalizer import NormalizeResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_normalize(result: NormalizeResult, show_unchanged: bool = False) -> str:
    lines = []
    lines.append(_c("Normalize Report", "1;36"))
    lines.append(
        f"  {result.key_count()} keys processed, "
        f"{_c(str(result.changed_count()), '1;33')} changed"
    )
    lines.append("")

    changed = [e for e in result.entries if e.was_changed]
    unchanged = [e for e in result.entries if not e.was_changed]

    if changed:
        lines.append(_c("Changed:", "1;33"))
        for entry in changed:
            parts = []
            if entry.key_changed:
                parts.append(
                    f"key: {_c(entry.original_key, '31')} → {_c(entry.key, '32')}"
                )
            if entry.value_changed:
                orig = repr(entry.original_value)
                norm = repr(entry.normalized_value)
                parts.append(f"value: {_c(orig, '31')} → {_c(norm, '32')}")
            lines.append(f"  {entry.key}  ({', '.join(parts)})")
    else:
        lines.append(_c("  No changes required.", "32"))

    if show_unchanged and unchanged:
        lines.append("")
        lines.append(_c("Unchanged:", "2"))
        for entry in unchanged:
            lines.append(f"  {_c(entry.key, '2')} = {entry.normalized_value}")

    return "\n".join(lines)
