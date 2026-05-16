"""Normalize environment variable keys and values to a canonical form."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NormalizeEntry:
    key: str
    original_key: str
    original_value: str
    normalized_value: str
    key_changed: bool
    value_changed: bool

    @property
    def was_changed(self) -> bool:
        return self.key_changed or self.value_changed


@dataclass
class NormalizeResult:
    entries: List[NormalizeEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.was_changed)

    def has_changes(self) -> bool:
        return self.changed_count() > 0

    def key_count(self) -> int:
        return len(self.entries)


def normalize_env(
    env: Dict[str, str],
    uppercase_keys: bool = True,
    strip_values: bool = True,
    replace_spaces_in_keys: bool = True,
    space_replacement: str = "_",
) -> NormalizeResult:
    """Normalize keys and values in *env* according to the requested rules."""
    entries: List[NormalizeEntry] = []
    normalized: Dict[str, str] = {}

    for original_key, original_value in env.items():
        key = original_key

        if replace_spaces_in_keys:
            key = key.replace(" ", space_replacement)

        if uppercase_keys:
            key = key.upper()

        value = original_value.strip() if strip_values else original_value

        entry = NormalizeEntry(
            key=key,
            original_key=original_key,
            original_value=original_value,
            normalized_value=value,
            key_changed=(key != original_key),
            value_changed=(value != original_value),
        )
        entries.append(entry)
        normalized[key] = value

    return NormalizeResult(entries=entries, env=normalized)
