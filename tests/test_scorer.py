"""Tests for envcast.scorer."""
import pytest
from envcast.scorer import score_env, ScoreResult, ScoreEntry


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "API_KEY": "supersecretkey123",
        "debug": "true",
        "EMPTY_VAR": "",
        "TOKEN": "abc",  # sensitive + short value
        "SPACED KEY": "value",
        "PADDED": "  hello  ",
    }


def test_score_env_returns_score_result(sample_env):
    result = score_env(sample_env)
    assert isinstance(result, ScoreResult)


def test_score_entry_count_matches_env(sample_env):
    result = score_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_clean_key_scores_100():
    result = score_env({"DATABASE_URL": "postgres://localhost/db"})
    assert result.entries[0].score == 100


def test_empty_value_deducts_points(sample_env):
    result = score_env(sample_env)
    entry = next(e for e in result.entries if e.key == "EMPTY_VAR")
    assert entry.score < 100
    reasons = [r for r, _ in entry.deductions]
    assert "empty value" in reasons


def test_lowercase_key_deducts_points(sample_env):
    result = score_env(sample_env)
    entry = next(e for e in result.entries if e.key == "debug")
    reasons = [r for r, _ in entry.deductions]
    assert "key not uppercase" in reasons


def test_spaced_key_deducts_points(sample_env):
    result = score_env(sample_env)
    entry = next(e for e in result.entries if e.key == "SPACED KEY")
    reasons = [r for r, _ in entry.deductions]
    assert "key contains spaces" in reasons


def test_sensitive_short_value_deducts_points(sample_env):
    result = score_env(sample_env)
    entry = next(e for e in result.entries if e.key == "TOKEN")
    reasons = [r for r, _ in entry.deductions]
    assert "sensitive key has short value" in reasons


def test_padded_value_deducts_points(sample_env):
    result = score_env(sample_env)
    entry = next(e for e in result.entries if e.key == "PADDED")
    reasons = [r for r, _ in entry.deductions]
    assert "value has leading whitespace" in reasons
    assert "value has trailing whitespace" in reasons


def test_score_never_goes_below_zero():
    # pile on many issues at once
    result = score_env({"bad key with spaces": ""})
    assert result.entries[0].score >= 0


def test_overall_score_is_average():
    result = score_env({"GOOD": "value", "bad": ""})
    assert 0 <= result.overall <= 100


def test_perfect_count():
    result = score_env({"GOOD": "value", "bad": ""})
    assert result.perfect_count == 1


def test_flagged_count():
    result = score_env({"GOOD": "value", "bad": ""})
    assert result.flagged_count == 1


def test_is_healthy_all_perfect():
    result = score_env({"A": "1", "B": "2"})
    assert result.is_healthy()


def test_is_healthy_fails_below_threshold():
    result = score_env({"a b c": ""})
    assert not result.is_healthy(threshold=80)


def test_empty_env_scores_100():
    result = score_env({})
    assert result.overall == 100
    assert result.is_healthy()
