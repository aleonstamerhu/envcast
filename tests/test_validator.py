"""Tests for envcast.validator."""

import textwrap
import pytest

from envcast.validator import load_schema, validate_env, ValidationResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def schema_file(tmp_path):
    content = textwrap.dedent("""\
        # Database settings
        DB_HOST
        DB_PORT=required
        DB_PASSWORD=optional
        SECRET_KEY
    """)
    p = tmp_path / ".env.schema"
    p.write_text(content)
    return str(p)


@pytest.fixture
def full_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_PASSWORD": "s3cr3t", "SECRET_KEY": "abc"}


# ---------------------------------------------------------------------------
# load_schema tests
# ---------------------------------------------------------------------------

def test_load_schema_marks_required_by_default(schema_file):
    schema = load_schema(schema_file)
    assert schema["DB_HOST"]["required"] is True


def test_load_schema_marks_explicit_required(schema_file):
    schema = load_schema(schema_file)
    assert schema["DB_PORT"]["required"] is True


def test_load_schema_marks_optional(schema_file):
    schema = load_schema(schema_file)
    assert schema["DB_PASSWORD"]["required"] is False


def test_load_schema_ignores_comments_and_blanks(schema_file):
    schema = load_schema(schema_file)
    assert len(schema) == 4


# ---------------------------------------------------------------------------
# validate_env tests
# ---------------------------------------------------------------------------

def test_validate_passes_with_all_required_keys(schema_file, full_env):
    schema = load_schema(schema_file)
    result = validate_env(full_env, schema)
    assert result.is_valid


def test_validate_detects_missing_required(schema_file):
    schema = load_schema(schema_file)
    env = {"DB_PORT": "5432", "SECRET_KEY": "abc"}  # DB_HOST missing
    result = validate_env(env, schema)
    assert not result.is_valid
    assert "DB_HOST" in result.missing_required


def test_validate_records_missing_optional(schema_file):
    schema = load_schema(schema_file)
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc"}
    result = validate_env(env, schema)
    assert result.is_valid
    assert "DB_PASSWORD" in result.missing_optional
    assert result.has_warnings


def test_validate_strict_flags_unknown_keys(schema_file, full_env):
    schema = load_schema(schema_file)
    env = {**full_env, "EXTRA_KEY": "value"}
    result = validate_env(env, schema, strict=True)
    assert result.is_valid
    assert "EXTRA_KEY" in result.unknown_keys


def test_validate_non_strict_ignores_unknown_keys(schema_file, full_env):
    schema = load_schema(schema_file)
    env = {**full_env, "EXTRA_KEY": "value"}
    result = validate_env(env, schema, strict=False)
    assert result.unknown_keys == []


def test_validate_missing_required_sorted(schema_file):
    schema = load_schema(schema_file)
    result = validate_env({}, schema)
    assert result.missing_required == sorted(result.missing_required)
