"""Tests for envcast.tagger and envcast.tag_formatter."""

from __future__ import annotations

import pytest

from envcast.tagger import TagEntry, TagResult, tag_env
from envcast.tag_formatter import format_tags


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "PORT": "8080",
    }


@pytest.fixture()
def tag_map() -> dict:
    return {
        "infra": ["DATABASE_URL", "PORT"],
        "security": ["SECRET_KEY"],
        "infra": ["DATABASE_URL", "PORT"],  # duplicate intentional – last write wins
    }


# ---------------------------------------------------------------------------
# tag_env
# ---------------------------------------------------------------------------

def test_tag_env_returns_tag_result(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    assert isinstance(result, TagResult)


def test_tag_env_entry_count_matches_env(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    assert len(result.entries) == len(sample_env)


def test_tag_env_correct_tags_applied(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    entry = next(e for e in result.entries if e.key == "DATABASE_URL")
    assert "infra" in entry.tags


def test_tag_env_untagged_key_has_empty_tags(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.tags == frozenset()


def test_tag_env_multiple_tags_on_single_key(sample_env):
    tm = {"backend": ["DATABASE_URL"], "critical": ["DATABASE_URL"]}
    result = tag_env(sample_env, tm)
    entry = next(e for e in result.entries if e.key == "DATABASE_URL")
    assert "backend" in entry.tags
    assert "critical" in entry.tags


def test_all_tags_returns_union(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    assert "infra" in result.all_tags()
    assert "security" in result.all_tags()


def test_keys_for_tag(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    infra_keys = result.keys_for_tag("infra")
    assert "DATABASE_URL" in infra_keys
    assert "PORT" in infra_keys


def test_tagged_count(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    # DATABASE_URL, PORT (infra) + SECRET_KEY (security) = 3 tagged
    assert result.tagged_count() == 3


def test_untagged_count(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    # Only DEBUG is untagged
    assert result.untagged_count() == 1


def test_empty_tag_map_all_untagged(sample_env):
    result = tag_env(sample_env, {})
    assert result.tagged_count() == 0
    assert result.untagged_count() == len(sample_env)


# ---------------------------------------------------------------------------
# format_tags
# ---------------------------------------------------------------------------

def test_format_includes_header(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    output = format_tags(result)
    assert "Environment Variable Tags" in output


def test_format_shows_tagged_key(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    output = format_tags(result)
    assert "DATABASE_URL" in output
    assert "infra" in output


def test_format_hide_untagged(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    output = format_tags(result, show_untagged=False)
    assert "DEBUG" not in output


def test_format_show_untagged_by_default(sample_env, tag_map):
    result = tag_env(sample_env, tag_map)
    output = format_tags(result)
    assert "DEBUG" in output
