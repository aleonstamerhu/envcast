"""Integration tests: 'envcast lint' CLI subcommand."""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent("""\
        DATABASE_URL=postgres://localhost/db
        DEBUG=false
        API_KEY=secret123
    """))
    return p


@pytest.fixture
def dirty_env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.dirty"
    p.write_text(textwrap.dedent("""\
        database_url=postgres://localhost/db
        DEBUG= bad_space 
        UNSET_VAR=${MISSING}
    """))
    return p


def _run(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "envcast", *args],
        capture_output=True,
        text=True,
    )


def test_build_parser_has_lint_subcommand():
    from envcast.cli import build_parser
    parser = build_parser()
    subparsers_actions = [
        a for a in parser._actions
        if hasattr(a, "_name_parser_map")
    ]
    assert any("lint" in a._name_parser_map for a in subparsers_actions)


def test_lint_clean_env_exits_zero(env_file):
    proc = _run("lint", str(env_file))
    assert proc.returncode == 0


def test_lint_dirty_env_exits_nonzero(dirty_env_file):
    proc = _run("lint", str(dirty_env_file))
    assert proc.returncode != 0


def test_lint_output_contains_report_header(env_file):
    proc = _run("lint", str(env_file))
    assert "Lint Report" in proc.stdout


def test_lint_dirty_output_contains_error_or_warning(dirty_env_file):
    proc = _run("lint", str(dirty_env_file))
    combined = proc.stdout + proc.stderr
    assert "ERROR" in combined or "WARN" in combined
