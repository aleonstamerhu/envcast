"""Format a TagResult for terminal display."""

from __future__ import annotations

from typing import List

from envcast.tagger import TagResult


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code* (reset appended)."""
    return f"\033[{code}m{text}\033[0m"


def format_tags(result: TagResult, *, show_untagged: bool = True) -> str:
    """Render *result* as a human-readable, coloured string.

    Args:
        result:        The :class:`TagResult` to render.
        show_untagged: When *False* entries with no tags are omitted.

    Returns:
        A multi-line string ready to be printed to a terminal.
    """
    lines: List[str] = []

    all_tags = sorted(result.all_tags())
    header = _c("Environment Variable Tags", "1;36")
    lines.append(header)
    lines.append(
        _c(
            f"  {result.tagged_count()} tagged  "
            f"{result.untagged_count()} untagged  "
            f"{len(all_tags)} distinct tag(s): "
            + ((", ".join(all_tags)) if all_tags else "(none)"),
            "2",
        )
    )
    lines.append("")

    for entry in result.entries:
        if not entry.tags and not show_untagged:
            continue

        tag_str = (
            "  ".join(_c(f"[{t}]", "1;33") for t in sorted(entry.tags))
            if entry.tags
            else _c("[untagged]", "2")
        )
        key_str = _c(entry.key, "1;32")
        lines.append(f"  {key_str} = {entry.value}  {tag_str}")

    if not result.entries:
        lines.append(_c("  (no entries)", "2"))

    return "\n".join(lines)
