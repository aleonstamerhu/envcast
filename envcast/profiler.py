"""Profile environment variables for sensitive value detection and pattern analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(secret|password|passwd|token|api[_-]?key|private[_-]?key|auth)", re.I),
    re.compile(r"(credential|cert|ssl|tls|hmac|jwt|oauth)", re.I),
]

_EMPTY_VALUE_RE = re.compile(r'^\s*$')
_URL_RE = re.compile(r'^https?://')
_PORT_RE = re.compile(r'^\d{2,5}$')


@dataclass
class ProfileResult:
    sensitive_keys: Set[str] = field(default_factory=set)
    empty_keys: Set[str] = field(default_factory=set)
    url_keys: Set[str] = field(default_factory=set)
    port_keys: Set[str] = field(default_factory=set)
    total_keys: int = 0

    @property
    def has_sensitive(self) -> bool:
        return bool(self.sensitive_keys)

    @property
    def has_empty(self) -> bool:
        return bool(self.empty_keys)

    def summary(self) -> Dict[str, int]:
        return {
            "total": self.total_keys,
            "sensitive": len(self.sensitive_keys),
            "empty": len(self.empty_keys),
            "urls": len(self.url_keys),
            "ports": len(self.port_keys),
        }


def _is_sensitive(key: str) -> bool:
    return any(p.search(key) for p in _SENSITIVE_PATTERNS)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse an environment dict and return a ProfileResult."""
    result = ProfileResult(total_keys=len(env))
    for key, value in env.items():
        if _is_sensitive(key):
            result.sensitive_keys.add(key)
        if _EMPTY_VALUE_RE.match(value):
            result.empty_keys.add(key)
        elif _URL_RE.match(value):
            result.url_keys.add(key)
        elif _PORT_RE.match(value):
            result.port_keys.add(key)
    return result
