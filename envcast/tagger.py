"""Tag environment variables with arbitrary labels for grouping and filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


@dataclass
class TagEntry:
    key: str
    value: str
    tags: FrozenSet[str]


@dataclass
class TagResult:
    entries: List[TagEntry] = field(default_factory=list)
    _tag_index: Dict[str, Set[str]] = field(default_factory=dict, repr=False)

    def all_tags(self) -> FrozenSet[str]:
        """Return the union of all tags across every entry."""
        result: Set[str] = set()
        for entry in self.entries:
            result |= entry.tags
        return frozenset(result)

    def keys_for_tag(self, tag: str) -> List[str]:
        """Return all keys that carry the given tag."""
        return [e.key for e in self.entries if tag in e.tags]

    def tagged_count(self) -> int:
        """Return the number of entries that have at least one tag."""
        return sum(1 for e in self.entries if e.tags)

    def untagged_count(self) -> int:
        """Return the number of entries with no tags."""
        return sum(1 for e in self.entries if not e.tags)


def tag_env(
    env: Dict[str, str],
    tag_map: Dict[str, List[str]],
) -> TagResult:
    """Attach tags to env keys according to *tag_map*.

    *tag_map* maps a tag label to a list of glob-free key names.
    Keys present in *env* but absent from every tag list receive no tags.

    Args:
        env:     Flat mapping of env-var key → value.
        tag_map: Mapping of tag name → list of keys that should carry that tag.

    Returns:
        A :class:`TagResult` with one :class:`TagEntry` per key in *env*.
    """
    # Build an inverted index: key → set of tags
    key_tags: Dict[str, Set[str]] = {}
    for tag, keys in tag_map.items():
        for k in keys:
            key_tags.setdefault(k, set()).add(tag)

    entries = [
        TagEntry(
            key=k,
            value=v,
            tags=frozenset(key_tags.get(k, set())),
        )
        for k, v in env.items()
    ]
    return TagResult(entries=entries)
