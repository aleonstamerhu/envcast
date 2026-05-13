"""Generate .env template files from a schema or existing env snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envcast.validator import load_schema


@dataclass
class TemplateEntry:
    key: str
    default: Optional[str]
    required: bool
    description: str = ""


@dataclass
class TemplateResult:
    entries: List[TemplateEntry] = field(default_factory=list)

    @property
    def required_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.required]

    @property
    def optional_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.required]


def build_template_from_schema(schema_path: str) -> TemplateResult:
    """Build a TemplateResult from a YAML schema file."""
    schema = load_schema(schema_path)
    entries: List[TemplateEntry] = []
    for key, meta in schema.items():
        entries.append(
            TemplateEntry(
                key=key,
                default=meta.get("default"),
                required=meta.get("required", True),
                description=meta.get("description", ""),
            )
        )
    return TemplateResult(entries=sorted(entries, key=lambda e: e.key))


def build_template_from_env(env: Dict[str, str]) -> TemplateResult:
    """Build a TemplateResult from an existing env dict (values become defaults)."""
    entries = [
        TemplateEntry(key=k, default=v, required=True)
        for k, v in sorted(env.items())
    ]
    return TemplateResult(entries=entries)


def render_template(result: TemplateResult, blank_values: bool = False) -> str:
    """Render a TemplateResult as a .env template string."""
    lines: List[str] = []
    for entry in result.entries:
        if entry.description:
            lines.append(f"# {entry.description}")
        if not entry.required:
            lines.append("# optional")
        value = "" if blank_values or entry.default is None else entry.default
        lines.append(f"{entry.key}={value}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
