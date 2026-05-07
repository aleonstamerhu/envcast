"""Tests for envcast.profile_formatter."""

import pytest
from envcast.profiler import profile_env
from envcast.profile_formatter import format_profile


@pytest.fixture
def full_env():
    return {
        "SECRET_KEY": "abc",
        "EMPTY_VAR": "",
        "PORT": "5432",
        "API_URL": "https://api.example.com",
        "APP": "myapp",
    }


def test_format_includes_summary_header(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "Profile Summary" in output
    assert "5 keys" in output


def test_format_lists_sensitive_keys(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "SECRET_KEY" in output


def test_format_lists_empty_keys(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "EMPTY_VAR" in output


def test_format_lists_url_keys(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "API_URL" in output


def test_format_lists_port_keys(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "PORT" in output


def test_format_no_sensitive_shows_none():
    env = {"APP": "foo", "DEBUG": "true"}
    output = format_profile(profile_env(env), color=False)
    assert "Sensitive keys: none" in output


def test_format_counts_in_footer(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "sensitive=" in output
    assert "empty=" in output


def test_format_with_color_contains_ansi(full_env):
    output = format_profile(profile_env(full_env), color=True)
    assert "\033[" in output


def test_format_without_color_no_ansi(full_env):
    output = format_profile(profile_env(full_env), color=False)
    assert "\033[" not in output
