"""Tests for envcast.renamer and envcast.rename_formatter."""

import pytest

from envcast.renamer import rename_keys, RenameResult
from envcast.rename_formatter import format_rename


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
    }


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_rename_applies_mapping(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.renamed
    assert result.renamed["DATABASE_HOST"] == "localhost"


def test_rename_removes_old_key_by_default(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" not in result.renamed


def test_rename_keep_original_retains_old_key(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"}, keep_original=True)
    assert "DB_HOST" in result.renamed
    assert "DATABASE_HOST" in result.renamed


def test_rename_skips_missing_key(sample_env):
    result = rename_keys(sample_env, {"MISSING_KEY": "NEW_KEY"})
    assert result.skipped_count == 1
    assert "NEW_KEY" not in result.renamed


def test_rename_count_reflects_successful_renames(sample_env):
    result = rename_keys(
        sample_env,
        {"DB_HOST": "DATABASE_HOST", "MISSING": "ALSO_MISSING"},
    )
    assert result.renamed_count == 1
    assert result.skipped_count == 1


def test_rename_has_renames_false_when_all_skip(sample_env):
    result = rename_keys(sample_env, {"NOPE": "STILL_NOPE"})
    assert not result.has_renames


def test_rename_preserves_untouched_keys(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_PORT" in result.renamed
    assert "APP_SECRET" in result.renamed


def test_rename_multiple_keys(sample_env):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(sample_env, mapping)
    assert result.renamed_count == 2
    assert "DATABASE_HOST" in result.renamed
    assert "DATABASE_PORT" in result.renamed


# ---------------------------------------------------------------------------
# format_rename
# ---------------------------------------------------------------------------

def test_format_includes_summary_header(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    output = format_rename(result, color=False)
    assert "Key Rename Summary" in output


def test_format_lists_renamed_key(sample_env):
    result = rename_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    output = format_rename(result, color=False)
    assert "DB_HOST" in output
    assert "DATABASE_HOST" in output


def test_format_lists_skipped_key(sample_env):
    result = rename_keys(sample_env, {"GHOST_KEY": "NEW_GHOST"})
    output = format_rename(result, color=False)
    assert "GHOST_KEY" in output
    assert "Skipped" in output
