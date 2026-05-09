"""Tests for envcast.redactor."""

import pytest

from envcast.redactor import (
    REDACT_PLACEHOLDER,
    RedactResult,
    _is_sensitive,
    redact_env,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_NAME": "envcast",
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
    }


# --- _is_sensitive -----------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DATABASE_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("API_KEY") is True


def test_is_sensitive_plain_key():
    assert _is_sensitive("APP_NAME") is False


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_Secret") is True


# --- redact_env --------------------------------------------------------------

def test_redact_replaces_sensitive_values(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["DATABASE_PASSWORD"] == REDACT_PLACEHOLDER
    assert result.redacted["API_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["AUTH_TOKEN"] == REDACT_PLACEHOLDER


def test_redact_preserves_non_sensitive_values(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["APP_NAME"] == "envcast"
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted["PORT"] == "8080"


def test_redact_original_unchanged(sample_env):
    result = redact_env(sample_env)
    assert result.original["DATABASE_PASSWORD"] == "s3cr3t"


def test_redact_count(sample_env):
    result = redact_env(sample_env)
    assert result.redacted_count == 3


def test_redact_has_redactions(sample_env):
    result = redact_env(sample_env)
    assert result.has_redactions is True


def test_redact_no_redactions_when_clean():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result.has_redactions is False
    assert result.redacted_count == 0


def test_redact_extra_keys(sample_env):
    result = redact_env(sample_env, extra_keys=["APP_NAME"])
    assert result.redacted["APP_NAME"] == REDACT_PLACEHOLDER
    assert "APP_NAME" in result.redacted_keys


def test_redact_custom_placeholder(sample_env):
    result = redact_env(sample_env, placeholder="<hidden>")
    assert result.redacted["API_KEY"] == "<hidden>"


def test_redact_empty_env():
    result = redact_env({})
    assert result.redacted == {}
    assert result.has_redactions is False
