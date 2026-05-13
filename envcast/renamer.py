"""Rename keys across an env dict using a mapping of old->new names."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameEntry:
    old_key: str
    new_key: str
    value: str
    skipped: bool = False  # True when old_key not present in env


@dataclass
class RenameResult:
    entries: List[RenameEntry] = field(default_factory=list)
    renamed: Dict[str, str] = field(default_factory=dict)  # final env

    @property
    def renamed_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    @property
    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    @property
    def has_renames(self) -> bool:
        return self.renamed_count > 0


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    keep_original: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *mapping*.

    Args:
        env: Source environment dictionary.
        mapping: ``{old_key: new_key}`` pairs.
        keep_original: When True, the old key is retained alongside the new one.

    Returns:
        A :class:`RenameResult` with the transformed env and a log of changes.
    """
    result_env: Dict[str, str] = dict(env)
    entries: List[RenameEntry] = []

    for old_key, new_key in mapping.items():
        if old_key not in env:
            entries.append(RenameEntry(old_key=old_key, new_key=new_key, value="", skipped=True))
            continue

        value = env[old_key]
        result_env[new_key] = value
        if not keep_original:
            result_env.pop(old_key, None)

        entries.append(RenameEntry(old_key=old_key, new_key=new_key, value=value, skipped=False))

    return RenameResult(entries=entries, renamed=result_env)
