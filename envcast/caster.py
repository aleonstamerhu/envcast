"""Type-cast environment variable values to inferred or specified Python types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _infer_type(value: str) -> str:
    """Return a label for the inferred type of *value*."""
    v = value.strip()
    if v.lower() in _BOOL_TRUE | _BOOL_FALSE:
        return "bool"
    try:
        int(v)
        return "int"
    except ValueError:
        pass
    try:
        float(v)
        return "float"
    except ValueError:
        pass
    return "str"


def _cast(value: str, type_hint: str) -> Any:
    """Cast *value* to the Python type described by *type_hint*."""
    if type_hint == "bool":
        return value.strip().lower() in _BOOL_TRUE
    if type_hint == "int":
        return int(value.strip())
    if type_hint == "float":
        return float(value.strip())
    return value


@dataclass
class CastEntry:
    key: str
    raw: str
    cast_value: Any
    type_label: str
    failed: bool = False
    error: Optional[str] = None


@dataclass
class CastResult:
    entries: List[CastEntry] = field(default_factory=list)

    @property
    def failed_count(self) -> int:
        return sum(1 for e in self.entries if e.failed)

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0

    def as_dict(self) -> Dict[str, Any]:
        return {e.key: e.cast_value for e in self.entries if not e.failed}


def cast_env(
    env: Dict[str, str],
    type_map: Optional[Dict[str, str]] = None,
) -> CastResult:
    """Cast each value in *env*, using *type_map* hints where provided."""
    type_map = type_map or {}
    result = CastResult()
    for key, raw in env.items():
        hint = type_map.get(key) or _infer_type(raw)
        try:
            cast_value = _cast(raw, hint)
            result.entries.append(CastEntry(key=key, raw=raw, cast_value=cast_value, type_label=hint))
        except (ValueError, TypeError) as exc:
            result.entries.append(
                CastEntry(key=key, raw=raw, cast_value=raw, type_label=hint, failed=True, error=str(exc))
            )
    return result
