"""encode_formatter.py – human-readable output for EncodeResult."""
from __future__ import annotations

from typing import List

from envcast.encoder import EncodeResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_encode(result: EncodeResult, show_unchanged: bool = False) -> str:
    lines: List[str] = []
    total = len(result.entries)
    changed = result.changed_count()

    lines.append(
        _c("1", f"Encode Report") + f"  encoding={_c('36', result.encoding)}"
        f"  keys={total}  encoded={_c('33', str(changed))}"
    )
    lines.append("─" * 60)

    for entry in result.entries:
        if not entry.changed and not show_unchanged:
            continue
        if entry.changed:
            label = _c("33", "ENC")
            detail = (
                f"  {_c('90', entry.original)}"
                f" → {_c('32', entry.encoded)}"
            )
        else:
            label = _c("90", "   ")
            detail = f"  {entry.original}"
        lines.append(f"  {label}  {_c('1', entry.key)}{detail}")

    lines.append("─" * 60)
    if changed == 0:
        lines.append(_c("32", "No values encoded."))
    else:
        lines.append(f"{_c('33', str(changed))} value(s) encoded with {result.encoding}.")

    return "\n".join(lines)
