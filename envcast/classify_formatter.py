"""Format ClassifyResult for terminal output."""
from __future__ import annotations

from typing import List

from envcast.classifier import ClassifyResult, UNCLASSIFIED


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


_CATEGORY_COLORS = {
    "database": 34,   # blue
    "auth": 31,       # red
    "network": 36,    # cyan
    "cloud": 33,      # yellow
    "logging": 35,    # magenta
    "feature": 32,    # green
    "email": 94,      # bright blue
    UNCLASSIFIED: 90, # dark grey
}


def format_classify(result: ClassifyResult) -> str:
    lines: List[str] = []
    total = len(result.entries)
    cat_count = result.category_count()
    unclass = result.unclassified_count()

    lines.append(_c(1, f"=== Classification Report ({total} keys, {cat_count} categories) ==="))
    lines.append("")

    for category in sorted(result.categories()):
        keys = result.keys_in_category(category)
        color = _CATEGORY_COLORS.get(category, 37)
        label = _c(color, f"[{category.upper()}]")
        lines.append(f"  {label} ({len(keys)} keys)")
        for key in sorted(keys):
            lines.append(f"    {_c(90, key)}")
        lines.append("")

    if result.has_unclassified():
        lines.append(_c(90, f"  {unclass} key(s) could not be classified."))
    else:
        lines.append(_c(32, "  All keys successfully classified."))

    return "\n".join(lines)
