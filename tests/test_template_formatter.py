"""Tests for envcast.template_formatter."""
from envcast.templater import TemplateEntry, TemplateResult
from envcast.template_formatter import format_template


def _make_result():
    return TemplateResult(
        entries=[
            TemplateEntry(key="DATABASE_URL", default=None, required=True, description="DB"),
            TemplateEntry(key="SECRET_KEY", default=None, required=True),
            TemplateEntry(key="DEBUG", default="false", required=False, description="toggle"),
            TemplateEntry(key="LOG_LEVEL", default="info", required=False),
        ]
    )


def test_format_includes_summary_header():
    out = format_template(_make_result(), color=False)
    assert "Template Summary" in out
    assert "4 keys" in out


def test_format_summary_counts_required_optional():
    out = format_template(_make_result(), color=False)
    assert "2 required" in out
    assert "2 optional" in out


def test_format_lists_required_keys():
    out = format_template(_make_result(), color=False)
    assert "DATABASE_URL" in out
    assert "SECRET_KEY" in out


def test_format_lists_optional_keys():
    out = format_template(_make_result(), color=False)
    assert "DEBUG" in out
    assert "LOG_LEVEL" in out


def test_format_has_required_section_label():
    out = format_template(_make_result(), color=False)
    assert "Required:" in out


def test_format_has_optional_section_label():
    out = format_template(_make_result(), color=False)
    assert "Optional:" in out


def test_format_color_false_no_escape_codes():
    out = format_template(_make_result(), color=False)
    assert "\033[" not in out


def test_format_color_true_has_escape_codes():
    out = format_template(_make_result(), color=True)
    assert "\033[" in out
