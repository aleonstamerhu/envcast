"""Key rotation: detect stale keys and suggest/apply rotated names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RotateEntry:
    key: str
    value: str
    suggested_key: Optional[str]
    reason: Optional[str]
    rotated: bool = False


@dataclass
class RotateResult:
    entries: List[RotateEntry] = field(default_factory=list)
    _rotated_env: Dict[str, str] = field(default_factory=dict, repr=False)

    @property
    def rotated_count(self) -> int:
        return sum(1 for e in self.entries if e.rotated)

    @property
    def has_rotations(self) -> bool:
        return self.rotated_count > 0

    @property
    def rotated_env(self) -> Dict[str, str]:
        return dict(self._rotated_env)

    def keys_with_suggestions(self) -> List[RotateEntry]:
        return [e for e in self.entries if e.suggested_key is not None]


# Patterns considered stale/legacy that should be rotated.
_STALE_SUFFIXES = ("_OLD", "_LEGACY", "_DEPRECATED", "_V1", "_BACKUP")
_STALE_PREFIXES = ("OLD_", "LEGACY_", "DEPRECATED_")


def _suggest_rotation(key: str) -> Optional[tuple[str, str]]:
    """Return (suggested_key, reason) or None if no rotation needed."""
    upper = key.upper()
    for suffix in _STALE_SUFFIXES:
        if upper.endswith(suffix):
            new_key = key[: len(key) - len(suffix)]
            return new_key, f"stale suffix '{suffix}'"
    for prefix in _STALE_PREFIXES:
        if upper.startswith(prefix):
            new_key = key[len(prefix) :]
            return new_key, f"stale prefix '{prefix}'"
    return None


def rotate_env(
    env: Dict[str, str],
    apply: bool = False,
    custom_mapping: Optional[Dict[str, str]] = None,
) -> RotateResult:
    """Analyse *env* for stale keys and optionally apply rotations.

    Args:
        env: Source environment variables.
        apply: When True, rename stale keys to their suggested replacements.
        custom_mapping: Explicit {old_key: new_key} overrides.
    """
    mapping = dict(custom_mapping or {})
    entries: List[RotateEntry] = []
    rotated_env: Dict[str, str] = {}

    for key, value in env.items():
        if key in mapping:
            new_key = mapping[key]
            entry = RotateEntry(
                key=key,
                value=value,
                suggested_key=new_key,
                reason="custom mapping",
                rotated=apply,
            )
            entries.append(entry)
            out_key = new_key if apply else key
            rotated_env[out_key] = value
        else:
            suggestion = _suggest_rotation(key)
            if suggestion:
                new_key, reason = suggestion
                entry = RotateEntry(
                    key=key,
                    value=value,
                    suggested_key=new_key,
                    reason=reason,
                    rotated=apply,
                )
                entries.append(entry)
                out_key = new_key if apply else key
                rotated_env[out_key] = value
            else:
                entries.append(
                    RotateEntry(key=key, value=value, suggested_key=None, reason=None)
                )
                rotated_env[key] = value

    result = RotateResult(entries=entries)
    result._rotated_env = rotated_env
    return result
