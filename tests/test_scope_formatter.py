"""Tests for envcast.scope_formatter."""

import pytest
from envcast.scoper import scope_env
from envcast.scope_formatter import format_scope


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envcast",
    }


@pytest.fixture()
def result(sample_env):
    return scope_env(sample_env, ["DB"])


def test_format_includes_header(result):
    output = format_scope(result)
    assert "Scope filter" in output


def test_format_shows_prefix_label(result):
    output = format_scope(result)
    assert "DB" in output


def test_format_shows_matched_count(result):
    output = format_scope(result)
    assert "matched" in output


def test_format_lists_matched_keys(result):
    output = format_scope(result)
    assert "DB_HOST" in output
    assert "DB_PORT" in output


def test_format_hides_unmatched_by_default(result):
    output = format_scope(result)
    assert "APP_NAME" not in output


def test_format_shows_unmatched_when_requested(result):
    output = format_scope(result, show_unmatched=True)
    assert "APP_NAME" in output


def test_format_no_matches_message():
    env = {"APP_NAME": "envcast"}
    result = scope_env(env, ["DB"])
    output = format_scope(result)
    assert "No keys matched" in output


def test_format_multiple_prefixes_in_header():
    env = {"DB_HOST": "h", "AWS_KEY": "k"}
    result = scope_env(env, ["DB", "AWS"])
    output = format_scope(result)
    assert "DB" in output
    assert "AWS" in output
