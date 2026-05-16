"""Integration-level CLI tests for the `scope` subcommand."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent("""\
            DB_HOST=localhost
            DB_PORT=5432
            AWS_KEY=AKIA123
            APP_NAME=envcast
            DEBUG=true
        """)
    )
    return p


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "envcast.cli", *args],
        capture_output=True,
        text=True,
    )


def test_build_parser_has_scope_subcommand():
    from envcast.cli import build_parser
    parser = build_parser()
    subparsers_actions = [
        a for a in parser._actions
        if hasattr(a, "_name_parser_map")
    ]
    assert subparsers_actions, "no subparsers registered"
    assert "scope" in subparsers_actions[0]._name_parser_map


def test_scope_command_exits_zero(env_file):
    proc = _run("scope", str(env_file), "--prefix", "DB")
    assert proc.returncode == 0


def test_scope_output_contains_matched_key(env_file):
    proc = _run("scope", str(env_file), "--prefix", "DB")
    assert "DB_HOST" in proc.stdout


def test_scope_output_excludes_unmatched_by_default(env_file):
    proc = _run("scope", str(env_file), "--prefix", "DB")
    assert "APP_NAME" not in proc.stdout


def test_scope_show_unmatched_flag(env_file):
    proc = _run("scope", str(env_file), "--prefix", "DB", "--show-unmatched")
    assert "APP_NAME" in proc.stdout
