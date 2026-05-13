"""Compare two snapshots and produce a structured comparison report."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envcast.snapshotter import Snapshot, compare_snapshots


@dataclass
class CompareEntry:
    key: str
    source_value: Optional[str]
    target_value: Optional[str]
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'


@dataclass
class CompareResult:
    source_label: str
    target_label: str
    entries: List[CompareEntry] = field(default_factory=list)

    @property
    def added(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def unchanged(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "unchanged"]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def difference_count(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


def compare_snapshots_report(
    source: Snapshot,
    target: Snapshot,
    include_unchanged: bool = False,
) -> CompareResult:
    """Produce a CompareResult from two Snapshot objects."""
    source_label = source.source or "source"
    target_label = target.source or "target"
    result = CompareResult(source_label=source_label, target_label=target_label)

    all_keys = set(source.env.keys()) | set(target.env.keys())

    for key in sorted(all_keys):
        src_val = source.env.get(key)
        tgt_val = target.env.get(key)

        if src_val is None:
            status = "added"
        elif tgt_val is None:
            status = "removed"
        elif src_val != tgt_val:
            status = "changed"
        else:
            status = "unchanged"

        if status == "unchanged" and not include_unchanged:
            continue

        result.entries.append(
            CompareEntry(key=key, source_value=src_val, target_value=tgt_val, status=status)
        )

    return result
