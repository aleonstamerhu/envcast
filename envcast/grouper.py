"""Group environment variables by prefix or custom mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupEntry:
    key: str
    value: str
    group: str


@dataclass
class GroupResult:
    entries: List[GroupEntry] = field(default_factory=list)
    _groups: Dict[str, List[GroupEntry]] = field(default_factory=dict, repr=False)

    def group_names(self) -> List[str]:
        return sorted(self._groups.keys())

    def keys_in_group(self, group: str) -> List[str]:
        return [e.key for e in self._groups.get(group, [])]

    def group_count(self) -> int:
        return len(self._groups)

    def ungrouped(self) -> List[GroupEntry]:
        return [e for e in self.entries if e.group == "(ungrouped)"]


def group_env(
    env: Dict[str, str],
    prefix_map: Optional[Dict[str, str]] = None,
    separator: str = "_",
) -> GroupResult:
    """Group *env* keys by their prefix.

    Args:
        env: Mapping of key -> value to group.
        prefix_map: Optional explicit mapping of prefix -> group label.
                    When *None* the prefix is derived automatically as the
                    portion of the key before the first *separator*.
        separator: Character used to split a key into prefix + rest.

    Returns:
        A :class:`GroupResult` with every key assigned to a group.
    """
    prefix_map = prefix_map or {}
    entries: List[GroupEntry] = []
    groups: Dict[str, List[GroupEntry]] = {}

    for key, value in env.items():
        # Determine group label
        if key in prefix_map:
            label = prefix_map[key]
        else:
            # Try to match any registered prefix
            matched_label: Optional[str] = None
            for prefix, lbl in prefix_map.items():
                if key.startswith(prefix + separator) or key == prefix:
                    matched_label = lbl
                    break
            if matched_label is None:
                # Auto-derive from first segment
                if separator in key:
                    matched_label = key.split(separator, 1)[0].upper()
                else:
                    matched_label = "(ungrouped)"
            label = matched_label

        entry = GroupEntry(key=key, value=value, group=label)
        entries.append(entry)
        groups.setdefault(label, []).append(entry)

    result = GroupResult(entries=entries)
    result._groups = groups
    return result
