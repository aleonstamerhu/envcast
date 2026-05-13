"""Resolve variable references within an env dict (e.g. VAR=${OTHER})."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    resolved: Dict[str, str]
    unresolved_keys: List[str] = field(default_factory=list)
    cycle_keys: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.unresolved_keys and not self.cycle_keys

    @property
    def summary(self) -> str:
        total = len(self.resolved)
        u = len(self.unresolved_keys)
        c = len(self.cycle_keys)
        return (
            f"{total} key(s) resolved"
            + (f", {u} unresolved reference(s)" if u else "")
            + (f", {c} cycle(s) detected" if c else "")
        )


def _refs_in(value: str) -> List[str]:
    return [m[0] or m[1] for m in _REF_RE.findall(value)]


def interpolate_env(
    env: Dict[str, str],
    external: Optional[Dict[str, str]] = None,
) -> InterpolateResult:
    """Expand ${VAR} / $VAR references in *env* values.

    Resolution order: env itself (after resolving), then *external*.
    Cycles and permanently unresolvable references are recorded.
    """
    external = external or {}
    resolved: Dict[str, str] = {}
    unresolved: List[str] = []
    cycle: List[str] = []

    def _resolve(key: str, visiting: frozenset) -> Optional[str]:
        if key in resolved:
            return resolved[key]
        if key in visiting:
            return None  # cycle
        raw = env.get(key)
        if raw is None:
            return external.get(key)
        refs = _refs_in(raw)
        if not refs:
            resolved[key] = raw
            return raw
        result = raw
        for ref in refs:
            ref_val = _resolve(ref, visiting | {key})
            if ref_val is None:
                return None
            result = re.sub(
                r"\$\{" + re.escape(ref) + r"\}|\$" + re.escape(ref) + r"(?![A-Za-z0-9_])",
                ref_val,
                result,
            )
        resolved[key] = result
        return result

    for key in env:
        val = _resolve(key, frozenset())
        if val is None:
            refs = _refs_in(env[key])
            visited: set = set()
            is_cycle = False
            stack = list(refs)
            while stack:
                r = stack.pop()
                if r == key or r in visited:
                    is_cycle = True
                    break
                visited.add(r)
                if r in env:
                    stack.extend(_refs_in(env[r]))
            if is_cycle:
                cycle.append(key)
            else:
                unresolved.append(key)
            resolved[key] = env[key]  # keep raw

    return InterpolateResult(
        resolved=resolved,
        unresolved_keys=unresolved,
        cycle_keys=cycle,
    )
