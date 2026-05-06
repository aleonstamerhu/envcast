"""Tests for envcast.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envcast.differ import diff_envs
from envcast.exporter import export_diff


@pytest.fixture()
def result():
    source = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true", "SECRET": "abc"}
    target = {"HOST": "prod.example.com", "PORT": "8080", "TIMEOUT": "30", "SECRET": "abc"}
    return diff_envs(source, target)


# ── JSON ──────────────────────────────────────────────────────────────────────

def test_export_json_structure(result):
    raw = export_diff(result, fmt="json")
    data = json.loads(raw)
    assert set(data.keys()) == {"only_in_source", "only_in_target", "changed", "matching"}


def test_export_json_only_in_source(result):
    data = json.loads(export_diff(result, fmt="json"))
    assert "DEBUG" in data["only_in_source"]
    assert data["only_in_source"]["DEBUG"] == "true"


def test_export_json_only_in_target(result):
    data = json.loads(export_diff(result, fmt="json"))
    assert "TIMEOUT" in data["only_in_target"]


def test_export_json_changed(result):
    data = json.loads(export_diff(result, fmt="json"))
    assert "HOST" in data["changed"]
    assert data["changed"]["HOST"]["source"] == "localhost"
    assert data["changed"]["HOST"]["target"] == "prod.example.com"


def test_export_json_matching(result):
    data = json.loads(export_diff(result, fmt="json"))
    assert "SECRET" in data["matching"]


# ── CSV ───────────────────────────────────────────────────────────────────────

def test_export_csv_has_header(result):
    raw = export_diff(result, fmt="csv")
    reader = csv.DictReader(io.StringIO(raw))
    assert reader.fieldnames == ["key", "status", "source_value", "target_value"]


def test_export_csv_rows(result):
    raw = export_diff(result, fmt="csv")
    rows = list(csv.DictReader(io.StringIO(raw)))
    statuses = {r["key"]: r["status"] for r in rows}
    assert statuses["DEBUG"] == "removed"
    assert statuses["TIMEOUT"] == "added"
    assert statuses["HOST"] == "changed"
    assert statuses["SECRET"] == "matching"


# ── dotenv ────────────────────────────────────────────────────────────────────

def test_export_dotenv_contains_all_keys(result):
    raw = export_diff(result, fmt="dotenv")
    keys = {line.split("=")[0] for line in raw.splitlines() if line}
    assert {"HOST", "PORT", "DEBUG", "SECRET", "TIMEOUT"} == keys


def test_export_dotenv_ends_with_newline(result):
    raw = export_diff(result, fmt="dotenv")
    assert raw.endswith("\n")


# ── invalid format ────────────────────────────────────────────────────────────

def test_export_invalid_format_raises(result):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_diff(result, fmt="xml")  # type: ignore[arg-type]
