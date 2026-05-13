"""Mask environment variable values for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "auth", "credential", "private_key", "access_key",
)

DEFAULT_MASK = "********"
_PARTIAL_VISIBLE = 4  # chars to reveal at start/end for partial mode


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def _mask_value(value: str, partial: bool = False) -> str:
    if not value:
        return value
    if not partial or len(value) <= _PARTIAL_VISIBLE * 2:
        return DEFAULT_MASK
    return value[:_PARTIAL_VISIBLE] + "****" + value[-_PARTIAL_VISIBLE:]


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def masked_count(self) -> int:
        return len(self.masked_keys)

    @property
    def has_masked(self) -> bool:
        return bool(self.masked_keys)


def mask_env(
    env: Dict[str, str],
    extra_keys: List[str] | None = None,
    partial: bool = False,
) -> MaskResult:
    """Return a MaskResult with sensitive values replaced by a mask string.

    Args:
        env: The environment mapping to process.
        extra_keys: Additional key names to treat as sensitive.
        partial: If True, reveal first/last few characters of the value.
    """
    sensitive_extras = {k.lower() for k in (extra_keys or [])}
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key) or key.lower() in sensitive_extras:
            masked[key] = _mask_value(value, partial=partial)
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
