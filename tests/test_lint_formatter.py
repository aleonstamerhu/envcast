"""Tests for envcast.lint_formatter."""
import pytest
from envcast.linter import LintIssue, LintResult
from envcast.lint_formatter import format_lint


@pytest.fixture
def clean_result():
    return LintResult(issues=[])


@pytest.fixture
def mixed_result():
    return LintResult(
        issues=[
            LintIssue("BAD_KEY", "error", "value has leading/trailing whitespace"),
            LintIssue("lower_key", "warning", "does not follow UPPER_SNAKE_CASE convention"),
        ]
    )


def test_format_includes_header(clean_result):
    output = format_lint(clean_result, color=False)
    assert "Lint Report" in output


def test_format_clean_shows_no_issues_message(clean_result):
    output = format_lint(clean_result, color=False)
    assert "No issues found" in output


def test_format_includes_error_label(mixed_result):
    output = format_lint(mixed_result, color=False)
    assert "[ERROR]" in output


def test_format_includes_warning_label(mixed_result):
    output = format_lint(mixed_result, color=False)
    assert "[WARN]" in output


def test_format_includes_key_name(mixed_result):
    output = format_lint(mixed_result, color=False)
    assert "BAD_KEY" in output
    assert "lower_key" in output


def test_format_includes_summary_line(mixed_result):
    output = format_lint(mixed_result, color=False)
    assert "Summary:" in output
    assert "1 error" in output
    assert "1 warning" in output


def test_format_summary_zero_when_clean(clean_result):
    output = format_lint(clean_result, color=False)
    assert "0 error" in output
    assert "0 warning" in output


def test_format_color_mode_does_not_crash(mixed_result):
    output = format_lint(mixed_result, color=True)
    assert "BAD_KEY" in output
