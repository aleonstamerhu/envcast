"""Apply a patch (set of key/value overrides) to an existing env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchEntry:
    key: str
    old_value: Optional[str]   # None  → key was absent before patch
    new_value: Optional[str]   # None  → key removed by patch
    action: str                # 'set' | 'unset' | 'noop'


@dataclass
class PatchResult:
    env: Dict[str, str]
    entries: List[PatchEntry] = field(default_factory=list)

    # ------------------------------------------------------------------ helpers
    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.action != "noop")

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    @property
    def set_count(self) -> int:
        return sum(1 for e in self.entries if e.action == "set")

    @property
    def unset_count(self) -> int:
        return sum(1 for e in self.entries if e.action == "unset")


def patch_env(
    base: Dict[str, str],
    patch: Dict[str, Optional[str]],
    *,
    allow_new: bool = True,
) -> PatchResult:
    """Apply *patch* on top of *base* and return a :class:`PatchResult`.

    Parameters
    ----------
    base:
        The original environment mapping.
    patch:
        Keys to add/update (value is a string) or remove (value is ``None``).
    allow_new:
        When *False*, keys that do not already exist in *base* are skipped
        (recorded with action ``'noop'``).
    """
    result_env: Dict[str, str] = dict(base)
    entries: List[PatchEntry] = []

    for key, new_value in patch.items():
        old_value = base.get(key)  # None if absent
        key_exists = key in base

        if new_value is None:
            # --- unset ---
            if key_exists:
                del result_env[key]
                entries.append(PatchEntry(key, old_value, None, "unset"))
            else:
                entries.append(PatchEntry(key, None, None, "noop"))
        else:
            # --- set ---
            if not key_exists and not allow_new:
                entries.append(PatchEntry(key, None, new_value, "noop"))
            elif old_value == new_value:
                entries.append(PatchEntry(key, old_value, new_value, "noop"))
            else:
                result_env[key] = new_value
                entries.append(PatchEntry(key, old_value, new_value, "set"))

    return PatchResult(env=result_env, entries=entries)
