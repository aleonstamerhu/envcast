"""Classify environment variable keys by inferred purpose/category."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "database": ["DB", "DATABASE", "POSTGRES", "MYSQL", "MONGO", "REDIS", "DSN"],
    "auth": ["AUTH", "JWT", "OAUTH", "SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "APIKEY"],
    "network": ["HOST", "PORT", "URL", "URI", "ENDPOINT", "ADDR", "ADDRESS", "DOMAIN"],
    "cloud": ["AWS", "GCP", "AZURE", "S3", "BUCKET", "REGION", "LAMBDA"],
    "logging": ["LOG", "LOGGING", "SENTRY", "DATADOG", "NEWRELIC", "DEBUG", "VERBOSE"],
    "feature": ["FEATURE", "FLAG", "ENABLE", "DISABLE", "TOGGLE"],
    "email": ["SMTP", "MAIL", "EMAIL", "SENDGRID", "MAILGUN"],
}

UNCLASSIFIED = "unclassified"


@dataclass
class ClassifyEntry:
    key: str
    value: str
    category: str


@dataclass
class ClassifyResult:
    entries: List[ClassifyEntry] = field(default_factory=list)

    def category_count(self) -> int:
        return len(self.categories())

    def categories(self) -> List[str]:
        seen = []
        for e in self.entries:
            if e.category not in seen:
                seen.append(e.category)
        return seen

    def keys_in_category(self, category: str) -> List[str]:
        return [e.key for e in self.entries if e.category == category]

    def unclassified_count(self) -> int:
        return sum(1 for e in self.entries if e.category == UNCLASSIFIED)

    def has_unclassified(self) -> bool:
        return self.unclassified_count() > 0


def _classify_key(key: str) -> str:
    upper = key.upper()
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in upper:
                return category
    return UNCLASSIFIED


def classify_env(env: Dict[str, str]) -> ClassifyResult:
    """Classify each key in *env* by inferred purpose category."""
    entries = [
        ClassifyEntry(key=k, value=v, category=_classify_key(k))
        for k, v in env.items()
    ]
    return ClassifyResult(entries=entries)
