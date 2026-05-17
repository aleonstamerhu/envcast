"""Tests for envcast.linter."""
import pytest
from envcast.linter import lint_env, LintResult


@pytest.fixture
def clean_env():
    return {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "false"}


def test_clean_env_produces_no_issues(clean_env):
    result = lint_env(clean_env)
    assert result.is_clean
    assert result.error_count == 0
    assert result.warning_count == 0


def test_lowercase_key_triggers_warning():
    result = lint_env({"database_url": "postgres://localhost/db"})
    assert any(i.key == "database_url" and i.level == "warning" for i in result.issues)


def test_mixed_case_key_triggers_warning():
    result = lint_env({"DatabaseUrl": "value"})
    assert result.warning_count >= 1


def test_empty_value_triggers_warning():
    result = lint_env({"MY_KEY": ""})
    assert any(i.level == "warning" and "empty" in i.message for i in result.issues)


def test_whitespace_value_triggers_error():
    result = lint_env({"MY_KEY": " value "})
    assert any(i.level == "error" and "whitespace" in i.message for i in result.issues)


def test_unresolved_placeholder_triggers_warning():
    result = lint_env({"MY_KEY": "${SOME_VAR}"})
    assert any("placeholder" in i.message for i in result.issues)


def test_case_collision_triggers_error():
    result = lint_env({"MY_KEY": "a", "my_key": "b"})
    assert any(i.level == "error" and "collide" in i.message for i in result.issues)


def test_multiple_issues_accumulate():
    result = lint_env({"bad key": " ", "GOOD_KEY": "${UNSET}"})
    assert len(result.issues) >= 2


def test_is_clean_false_when_errors_present():
    result = lint_env({"MY_KEY": "  leading"})
    assert not result.is_clean


def test_errors_and_warnings_partitioned_correctly():
    result = lint_env({"lower": "", "MY_KEY": " bad "})
    assert all(i.level == "error" for i in result.errors)
    assert all(i.level == "warning" for i in result.warnings)


def test_error_count_matches_errors_list():
    """Ensure error_count is consistent with the errors list length."""
    result = lint_env({"MY_KEY": " bad ", "my_key": "collision"})
    assert result.error_count == len(result.errors)


def test_warning_count_matches_warnings_list():
    """Ensure warning_count is consistent with the warnings list length."""
    result = lint_env({"lower": "", "MixedCase": "value"})
    assert result.warning_count == len(result.warnings)
