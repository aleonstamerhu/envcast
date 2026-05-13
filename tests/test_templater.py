"""Tests for envcast.templater."""
import textwrap
import pytest

from envcast.templater import (
    TemplateEntry,
    TemplateResult,
    build_template_from_env,
    build_template_from_schema,
    render_template,
)


@pytest.fixture()
def schema_file(tmp_path):
    content = textwrap.dedent("""\
        DATABASE_URL:
          required: true
          description: Postgres connection string
        SECRET_KEY:
          required: true
        DEBUG:
          required: false
          default: "false"
          description: Enable debug mode
    """)
    p = tmp_path / "schema.yaml"
    p.write_text(content)
    return str(p)


def test_build_from_schema_required_keys(schema_file):
    result = build_template_from_schema(schema_file)
    assert "DATABASE_URL" in result.required_keys
    assert "SECRET_KEY" in result.required_keys


def test_build_from_schema_optional_keys(schema_file):
    result = build_template_from_schema(schema_file)
    assert "DEBUG" in result.optional_keys


def test_build_from_schema_description(schema_file):
    result = build_template_from_schema(schema_file)
    entry = next(e for e in result.entries if e.key == "DATABASE_URL")
    assert entry.description == "Postgres connection string"


def test_build_from_schema_default(schema_file):
    result = build_template_from_schema(schema_file)
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.default == "false"


def test_build_from_env_uses_values_as_defaults():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = build_template_from_env(env)
    keys = {e.key: e.default for e in result.entries}
    assert keys["HOST"] == "localhost"
    assert keys["PORT"] == "5432"


def test_build_from_env_all_required():
    env = {"A": "1", "B": "2"}
    result = build_template_from_env(env)
    assert all(e.required for e in result.entries)


def test_render_template_includes_keys(schema_file):
    result = build_template_from_schema(schema_file)
    rendered = render_template(result)
    assert "DATABASE_URL=" in rendered
    assert "SECRET_KEY=" in rendered


def test_render_template_blank_values(schema_file):
    result = build_template_from_schema(schema_file)
    rendered = render_template(result, blank_values=True)
    for line in rendered.splitlines():
        if "=" in line and not line.startswith("#"):
            assert line.endswith("=")


def test_render_template_includes_description(schema_file):
    result = build_template_from_schema(schema_file)
    rendered = render_template(result)
    assert "# Postgres connection string" in rendered


def test_render_template_marks_optional(schema_file):
    result = build_template_from_schema(schema_file)
    rendered = render_template(result)
    assert "# optional" in rendered
