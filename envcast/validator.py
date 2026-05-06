"""Validate environment variables against a schema of required keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.missing_required) == 0

    @property
    def has_warnings(self) -> bool:
        return bool(self.missing_optional or self.unknown_keys)


def load_schema(schema_path: str) -> Dict[str, dict]:
    """Load a schema file (.env.schema) defining required/optional keys.

    Schema format (one key per line):
        KEY_NAME          -> required by default
        KEY_NAME=required -> explicitly required
        KEY_NAME=optional -> optional
    """
    schema: Dict[str, dict] = {}
    with open(schema_path, "r") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, qualifier = line.partition("=")
                qualifier = qualifier.strip().lower()
            else:
                key = line
                qualifier = "required"
            schema[key.strip()] = {"required": qualifier != "optional"}
    return schema


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, dict],
    strict: bool = False,
) -> ValidationResult:
    """Validate *env* against *schema*.

    Args:
        env: Mapping of key -> value to validate.
        schema: Mapping of key -> {"required": bool} produced by load_schema.
        strict: When True, keys present in env but absent from schema are
                recorded as unknown_keys.

    Returns:
        A ValidationResult instance.
    """
    result = ValidationResult()

    for key, meta in schema.items():
        if key not in env:
            if meta["required"]:
                result.missing_required.append(key)
            else:
                result.missing_optional.append(key)

    if strict:
        for key in env:
            if key not in schema:
                result.unknown_keys.append(key)

    result.missing_required.sort()
    result.missing_optional.sort()
    result.unknown_keys.sort()
    return result
