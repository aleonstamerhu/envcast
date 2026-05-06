"""Tests for envcast.formatter module."""

import pytest

from envcast.differ import DiffResult
from envcast.formatter import format_diff


@pytest.fixture
def sample_result():
    return DiffResult(
        only_in_source={"SECRET": "abc"},
        only_in_target={"DEBUG": "true"},
        changed={"APP_ENV": ("production", "staging")},
        matching={"PORT": "8080"},
    )


def test_format_includes_removed_key(sample_result):
    output = format_diff(sample_result, use_color=False)
    assert "- SECRET=abc" in output


def test_format_includes_added_key(sample_result):
    output = format_diff(sample_result, use_color=False)
    assert "+ DEBUG=true" in output


def test_format_includes_changed_key(sample_result):
    output = format_diff(sample_result, use_color=False)
    assert "~ APP_ENV" in output
    assert "production" in output
    assert "staging" in output


def test_format_hides_matching_by_default(sample_result):
    output = format_diff(sample_result, use_color=False)
    assert "PORT" not in output


def test_format_shows_matching_when_requested(sample_result):
    output = format_diff(sample_result, use_color=False, show_matching=True)
    assert "PORT=8080" in output


def test_format_masks_values(sample_result):
    output = format_diff(sample_result, use_color=False, mask_values=True)
    assert "abc" not in output
    assert "***" in output


def test_format_no_differences_message():
    result = DiffResult(matching={"KEY": "val"})
    output = format_diff(result, use_color=False)
    assert "No differences found" in output


def test_format_custom_labels(sample_result):
    output = format_diff(sample_result, source_label="prod", target_label="dev", use_color=False)
    assert "prod" in output
    assert "dev" in output


def test_format_with_color_contains_ansi(sample_result):
    output = format_diff(sample_result, use_color=True)
    assert "\033[" in output
