"""Terminal formatter for ScopeResult."""

from __future__ import annotations

from typing import List

from envcast.scoper import ScopeResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_scope(result: ScopeResult, *, show_unmatched: bool = False) -> str:
    lines: List[str] = []

    scopes_label = ", ".join(result.scopes_requested) or "(none)"
    lines.append(_c("1", f"Scope filter — prefixes: {scopes_label}"))
    lines.append(
        f"  matched: {_c('32', str(result.matched_count()))}  "
        f"unmatched: {_c('33', str(result.unmatched_count()))}"
    )
    lines.append("")

    matched = [e for e in result.entries if e.scope is not None]
    if matched:
        lines.append(_c("1;34", "Matched keys:"))
        for entry in sorted(matched, key=lambda e: e.key):
            scope_tag = _c("36", f"[{entry.scope}]")
            lines.append(f"  {scope_tag} {entry.key} = {entry.value}")
    else:
        lines.append(_c("33", "  No keys matched the requested scopes."))

    if show_unmatched:
        unmatched = [e for e in result.entries if e.scope is None]
        if unmatched:
            lines.append("")
            lines.append(_c("1;90", "Unmatched keys:"))
            for entry in sorted(unmatched, key=lambda e: e.key):
                lines.append(f"  {_c('90', entry.key)} = {_c('90', entry.value)}")

    return "\n".join(lines)
