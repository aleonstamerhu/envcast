"""Integration-style tests for the 'profile' CLI command."""

import json
import textwrap
from pathlib import Path
import pytest
from envcast.cli import build_parser, main


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent("""\
        APP_NAME=myapp
        SECRET_TOKEN=supersecret
        DATABASE_URL=https://db.example.com
        PORT=5432
        EMPTY_VAR=
        """)
    )
    return str(p)


def test_build_parser_has_profile_subcommand():
    parser = build_parser()
    # Should not raise
    args = parser.parse_args(["profile", "some.env"])
    assert args.command == "profile"


def test_profile_command_exits_zero(env_file, capsys):
    parser = build_parser()
    args = parser.parse_args(["profile", env_file])
    try:
        main(argv=["profile", env_file])
    except SystemExit as exc:
        assert exc.code == 0


def test_profile_output_contains_summary(env_file, capsys):
    try:
        main(argv=["profile", env_file])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "Profile Summary" in captured.out


def test_profile_output_flags_sensitive(env_file, capsys):
    try:
        main(argv=["profile", env_file])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "SECRET_TOKEN" in captured.out


def test_profile_output_flags_empty(env_file, capsys):
    try:
        main(argv=["profile", env_file])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "EMPTY_VAR" in captured.out
