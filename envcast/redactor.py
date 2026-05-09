"""Redact sensitive values in env dicts before display or export."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

# Keys whose values should be masked
_SENSITIVE_PATTERNS: List[str] = [
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "private_key", "auth", "credential", "access_key", "signing_key",
]

REDACT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: Set[str] = field(default_factory=set)

    @property
    def redacted_count(self) -> int:
        return len(self.redacted_keys)

    @property
    def has_redactions(self) -> bool:
        return bool(self.redacted_keys)


def _is_sensitive(key: str) -> bool:
    """Return True if *key* matches any known sensitive pattern."""
    lower = key.lower()
    return any(pattern in lower for pattern in _SENSITIVE_PATTERNS)


def redact_env(
    env: Dict[str, str],
    extra_keys: List[str] | None = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by *placeholder*.

    Args:
        env: The environment mapping to redact.
        extra_keys: Additional key names (case-insensitive) to always redact.
        placeholder: The string to substitute for redacted values.
    """
    extra: Set[str] = {k.lower() for k in (extra_keys or [])}
    redacted: Dict[str, str] = {}
    redacted_keys: Set[str] = set()

    for key, value in env.items():
        if _is_sensitive(key) or key.lower() in extra:
            redacted[key] = placeholder
            redacted_keys.add(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )
