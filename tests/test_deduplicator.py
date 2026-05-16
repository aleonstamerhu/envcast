"""Tests for envcast.deduplicator and envcast.dedup_formatter."""
import pytest

from envcast.deduplicator import DeduplicateResult, DuplicateEntry, deduplicate_env
from envcast.dedup_formatter import format_dedup


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DATABASE_HOST": "localhost",
        "API_URL": "https://api.example.com",
        "SERVICE_URL": "https://api.example.com",
        "EXTRA_URL": "https://api.example.com",
        "UNIQUE_KEY": "only-me",
    }


def test_deduplicate_returns_result_type(sample_env):
    result = deduplicate_env(sample_env)
    assert isinstance(result, DeduplicateResult)


def test_deduplicate_detects_duplicates(sample_env):
    result = deduplicate_env(sample_env)
    assert result.has_duplicates


def test_duplicate_count(sample_env):
    result = deduplicate_env(sample_env)
    # Two distinct values each shared by multiple keys
    assert result.duplicate_count == 2


def test_keep_first_retains_alphabetically_first(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_first")
    # "API_URL" < "EXTRA_URL" < "SERVICE_URL"
    assert "API_URL" in result.env
    assert "SERVICE_URL" not in result.env
    assert "EXTRA_URL" not in result.env


def test_keep_last_retains_alphabetically_last(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_last")
    assert "SERVICE_URL" in result.env
    assert "API_URL" not in result.env


def test_report_only_leaves_env_unchanged(sample_env):
    result = deduplicate_env(sample_env, strategy="report_only")
    assert result.env == sample_env
    assert result.has_duplicates


def test_removed_keys_keep_first(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_first")
    removed = result.removed_keys
    assert "SERVICE_URL" in removed
    assert "EXTRA_URL" in removed
    assert "API_URL" not in removed


def test_removed_keys_report_only_is_empty(sample_env):
    result = deduplicate_env(sample_env, strategy="report_only")
    assert result.removed_keys == []


def test_unique_key_preserved(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_first")
    assert "UNIQUE_KEY" in result.env
    assert result.env["UNIQUE_KEY"] == "only-me"


def test_no_duplicates_env():
    env = {"A": "1", "B": "2", "C": "3"}
    result = deduplicate_env(env)
    assert not result.has_duplicates
    assert result.env == env


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate_env({"A": "1"}, strategy="bogus")


def test_entry_key_count():
    entry = DuplicateEntry(value="x", keys=["A", "B", "C"])
    assert entry.key_count == 3


# --- formatter tests ---

def test_format_includes_header(sample_env):
    result = deduplicate_env(sample_env)
    output = format_dedup(result, color=False)
    assert "Deduplication Report" in output


def test_format_no_duplicates_message():
    result = deduplicate_env({"A": "1", "B": "2"})
    output = format_dedup(result, color=False)
    assert "No duplicate values found" in output


def test_format_lists_duplicate_group(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_first")
    output = format_dedup(result, color=False)
    assert "localhost" in output
    assert "DB_HOST" in output


def test_format_shows_removed_count(sample_env):
    result = deduplicate_env(sample_env, strategy="keep_first")
    output = format_dedup(result, color=False)
    assert "Removed" in output
