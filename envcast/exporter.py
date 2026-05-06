"""Export environment diffs to various output formats (JSON, CSV, dotenv)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envcast.differ import DiffResult

ExportFormat = Literal["json", "csv", "dotenv"]


def export_diff(result: DiffResult, fmt: ExportFormat = "json") -> str:
    """Serialize a DiffResult to the requested format string."""
    if fmt == "json":
        return _to_json(result)
    elif fmt == "csv":
        return _to_csv(result)
    elif fmt == "dotenv":
        return _to_dotenv(result)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")


def _to_json(result: DiffResult) -> str:
    payload = {
        "only_in_source": {k: result.source[k] for k in sorted(result.only_in_source)},
        "only_in_target": {k: result.target[k] for k in sorted(result.only_in_target)},
        "changed": {
            k: {"source": result.source[k], "target": result.target[k]}
            for k in sorted(result.changed)
        },
        "matching": sorted(result.matching),
    }
    return json.dumps(payload, indent=2)


def _to_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "source_value", "target_value"])

    for key in sorted(result.only_in_source):
        writer.writerow([key, "removed", result.source[key], ""])
    for key in sorted(result.only_in_target):
        writer.writerow([key, "added", "", result.target[key]])
    for key in sorted(result.changed):
        writer.writerow([key, "changed", result.source[key], result.target[key]])
    for key in sorted(result.matching):
        writer.writerow([key, "matching", result.source[key], result.target[key]])

    return buf.getvalue()


def _to_dotenv(result: DiffResult) -> str:
    """Emit a dotenv file representing the merged/target state after diff."""
    lines: list[str] = []
    all_keys = sorted(
        result.only_in_source
        | result.only_in_target
        | result.changed
        | result.matching
    )
    merged = {**result.source, **result.target}
    for key in all_keys:
        value = merged.get(key, "")
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
