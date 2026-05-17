"""encoder.py – encode environment variable values to a target format (base64, url, hex)."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, List, Literal

Encoding = Literal["base64", "url", "hex"]


@dataclass
class EncodeEntry:
    key: str
    original: str
    encoded: str
    encoding: str
    changed: bool


@dataclass
class EncodeResult:
    entries: List[EncodeEntry] = field(default_factory=list)
    encoding: str = "base64"

    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    def has_changes(self) -> bool:
        return self.changed_count() > 0

    def to_env(self) -> Dict[str, str]:
        return {e.key: e.encoded for e in self.entries}


def _encode_value(value: str, encoding: Encoding) -> str:
    if encoding == "base64":
        return base64.b64encode(value.encode()).decode()
    if encoding == "url":
        return urllib.parse.quote(value, safe="")
    if encoding == "hex":
        return value.encode().hex()
    raise ValueError(f"Unknown encoding: {encoding}")


def encode_env(
    env: Dict[str, str],
    encoding: Encoding = "base64",
    keys: List[str] | None = None,
) -> EncodeResult:
    """Encode values in *env*.

    If *keys* is provided only those keys are encoded; all others are passed
    through unchanged.
    """
    result = EncodeResult(encoding=encoding)
    for key, value in env.items():
        if keys is None or key in keys:
            encoded = _encode_value(value, encoding)
            changed = encoded != value
        else:
            encoded = value
            changed = False
        result.entries.append(
            EncodeEntry(
                key=key,
                original=value,
                encoded=encoded,
                encoding=encoding if (keys is None or key in keys) else "none",
                changed=changed,
            )
        )
    return result
