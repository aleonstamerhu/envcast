"""envcast.pinner — Pin environment variable values to a lockfile for reproducible deployments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import hashlib


@dataclass
class PinEntry:
    key: str
    value: str
    pinned_value: str
    changed: bool


@dataclass
class PinResult:
    entries: List[PinEntry] = field(default_factory=list)
    source: Optional[str] = None

    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    @property
    def has_drift(self) -> bool:
        return self.changed_count > 0

    @property
    def pinned_env(self) -> Dict[str, str]:
        return {e.key: e.pinned_value for e in self.entries}


def _checksum(env: Dict[str, str]) -> str:
    """Return a stable SHA-256 hex digest of the env mapping."""
    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def load_lockfile(path: str) -> Dict[str, str]:
    """Load a previously written lockfile.  Returns empty dict if not found."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("env", {})
    except FileNotFoundError:
        return {}


def write_lockfile(path: str, env: Dict[str, str]) -> None:
    """Persist *env* to *path* as a JSON lockfile with a checksum."""
    payload = {"env": env, "checksum": _checksum(env)}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")


def pin_env(
    current: Dict[str, str],
    locked: Dict[str, str],
    source: Optional[str] = None,
) -> PinResult:
    """Compare *current* env against *locked* snapshot.

    Each key present in *current* gets a :class:`PinEntry`.  If the key
    exists in *locked* its pinned_value is the locked value; otherwise the
    current value is used (new pin).  ``changed`` is ``True`` when the live
    value differs from the pin.
    """
    entries: List[PinEntry] = []
    for key, value in sorted(current.items()):
        pinned = locked.get(key, value)
        entries.append(
            PinEntry(key=key, value=value, pinned_value=pinned, changed=(value != pinned))
        )
    return PinResult(entries=entries, source=source)
