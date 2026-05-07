"""Tests for envcast.profiler."""

import pytest
from envcast.profiler import profile_env, ProfileResult


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "",
        "PORT": "8080",
        "BASE_URL": "https://example.com",
        "PLAIN": "  ",
    }


def test_profile_detects_sensitive_keys(sample_env):
    result = profile_env(sample_env)
    assert "DATABASE_PASSWORD" in result.sensitive_keys
    assert "API_KEY" in result.sensitive_keys


def test_profile_non_sensitive_not_flagged(sample_env):
    result = profile_env(sample_env)
    assert "APP_NAME" not in result.sensitive_keys
    assert "PORT" not in result.sensitive_keys


def test_profile_detects_empty_values(sample_env):
    result = profile_env(sample_env)
    assert "DEBUG" in result.empty_keys
    assert "PLAIN" in result.empty_keys


def test_profile_detects_url_values(sample_env):
    result = profile_env(sample_env)
    assert "BASE_URL" in result.url_keys


def test_profile_detects_port_values(sample_env):
    result = profile_env(sample_env)
    assert "PORT" in result.port_keys


def test_profile_total_keys(sample_env):
    result = profile_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_has_sensitive_true(sample_env):
    result = profile_env(sample_env)
    assert result.has_sensitive is True


def test_has_sensitive_false():
    result = profile_env({"APP_NAME": "foo", "DEBUG": "true"})
    assert result.has_sensitive is False


def test_has_empty_true(sample_env):
    result = profile_env(sample_env)
    assert result.has_empty is True


def test_summary_keys(sample_env):
    result = profile_env(sample_env)
    summary = result.summary()
    assert set(summary.keys()) == {"total", "sensitive", "empty", "urls", "ports"}
    assert summary["total"] == len(sample_env)


def test_empty_env():
    result = profile_env({})
    assert result.total_keys == 0
    assert not result.has_sensitive
    assert not result.has_empty
