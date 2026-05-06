"""Sync environment variables from a source to one or more target .env files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envcast.differ import diff_envs, DiffResult


@dataclass
class SyncResult:
    target_path: str
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return len(self.added) + len(self.updated)


def sync_env(
    source: Dict[str, str],
    target: Dict[str, str],
    target_path: str,
    overwrite: bool = True,
    dry_run: bool = False,
    only_missing: bool = False,
) -> SyncResult:
    """Sync keys from source into target env file.

    Args:
        source: Source environment variables.
        target: Target environment variables.
        target_path: Path to the target .env file to write.
        overwrite: If True, update keys whose values differ.
        dry_run: If True, compute changes but do not write.
        only_missing: If True, only add keys absent in target.

    Returns:
        SyncResult describing what was added, updated, or skipped.
    """
    result = SyncResult(target_path=target_path)
    diff: DiffResult = diff_envs(source, target)

    merged = dict(target)

    for key in diff.only_in_source:
        merged[key] = source[key]
        result.added.append(key)

    for key in diff.changed:
        if only_missing:
            result.skipped.append(key)
        elif overwrite:
            merged[key] = source[key]
            result.updated.append(key)
        else:
            result.skipped.append(key)

    if not dry_run and result.changed_count > 0:
        _write_env_file(target_path, merged)

    return result


def _write_env_file(path: str, env: Dict[str, str]) -> None:
    """Write an env dict to a .env file.

    Raises:
        OSError: If the file cannot be written (e.g. permission denied).
    """
    target = Path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [f'{key}="{value}"\n' for key, value in sorted(env.items())]
        target.write_text("".join(lines), encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Failed to write env file '{path}': {exc}") from exc
