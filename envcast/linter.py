"""Lint environment variable keys and values for common issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_NAMING_PATTERN = __import__("re").compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass
class LintIssue:
    key: str
    level: str          # 'error' | 'warning'
    message: str


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


def lint_env(env: Dict[str, str]) -> LintResult:
    """Run all lint checks against *env* and return a LintResult."""
    result = LintResult()

    for key, value in env.items():
        # Naming convention: UPPER_SNAKE_CASE
        if not _NAMING_PATTERN.match(key):
            result.issues.append(
                LintIssue(key, "warning", f"Key '{key}' does not follow UPPER_SNAKE_CASE convention")
            )

        # Empty value
        if value == "":
            result.issues.append(
                LintIssue(key, "warning", f"Key '{key}' has an empty value")
            )

        # Whitespace leakage
        if value != value.strip():
            result.issues.append(
                LintIssue(key, "error", f"Key '{key}' value has leading/trailing whitespace")
            )

        # Unresolved placeholder  ${VAR}
        if __import__("re").search(r"\$\{[^}]+\}", value):
            result.issues.append(
                LintIssue(key, "warning", f"Key '{key}' value contains an unresolved placeholder")
            )

        # Duplicate-looking keys (lowercase collision)
        # Checked at env level after the loop

    # Detect keys that differ only by case
    lower_map: Dict[str, List[str]] = {}
    for key in env:
        lower_map.setdefault(key.lower(), []).append(key)
    for lower_key, keys in lower_map.items():
        if len(keys) > 1:
            result.issues.append(
                LintIssue(keys[0], "error", f"Keys {keys} collide when compared case-insensitively")
            )

    return result
