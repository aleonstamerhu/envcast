"""Integration tests for the 'template' subcommand in envcast CLI."""
import subprocess
import sys
import textwrap
import pytest


@pytest.fixture()
def schema_file(tmp_path):
    content = textwrap.dedent("""\
        APP_PORT:
          required: true
          description: HTTP port
        APP_ENV:
          required: false
          default: production
    """)
    p = tmp_path / "schema.yaml"
    p.write_text(content)
    return str(p)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=8080\n")
    return str(p)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envcast", *args],
        capture_output=True,
        text=True,
    )


def test_build_parser_has_template_subcommand():
    from envcast.cli import build_parser
    parser = build_parser()
    subparsers_actions = [
        a for a in parser._actions
        if hasattr(a, "_name_parser_map")
    ]
    assert any(
        "template" in a._name_parser_map
        for a in subparsers_actions
    )


def test_template_from_schema_exits_zero(schema_file):
    result = _run("template", "--schema", schema_file)
    assert result.returncode == 0


def test_template_from_schema_output_contains_key(schema_file):
    result = _run("template", "--schema", schema_file)
    assert "APP_PORT" in result.stdout


def test_template_from_env_exits_zero(env_file):
    result = _run("template", "--source", env_file)
    assert result.returncode == 0


def test_template_render_flag_writes_dotenv(schema_file, tmp_path):
    out_file = tmp_path / "out.env"
    result = _run("template", "--schema", schema_file, "--render", str(out_file))
    assert result.returncode == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "APP_PORT=" in content
