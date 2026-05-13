"""Tests for envcast.interpolator and envcast.interpolate_formatter."""
import pytest

from envcast.interpolator import interpolate_env, InterpolateResult
from envcast.interpolate_formatter import format_interpolate


@pytest.fixture
def simple_env():
    return {
        "BASE": "/opt/app",
        "LOG_DIR": "${BASE}/logs",
        "CACHE_DIR": "$BASE/cache",
        "PLAIN": "hello",
    }


def test_resolves_braced_reference(simple_env):
    result = interpolate_env(simple_env)
    assert result.resolved["LOG_DIR"] == "/opt/app/logs"


def test_resolves_unbraced_reference(simple_env):
    result = interpolate_env(simple_env)
    assert result.resolved["CACHE_DIR"] == "/opt/app/cache"


def test_plain_value_unchanged(simple_env):
    result = interpolate_env(simple_env)
    assert result.resolved["PLAIN"] == "hello"


def test_is_clean_when_all_resolved(simple_env):
    result = interpolate_env(simple_env)
    assert result.is_clean
    assert result.unresolved_keys == []
    assert result.cycle_keys == []


def test_unresolved_recorded():
    env = {"URL": "http://${HOST}:${PORT}/path"}
    result = interpolate_env(env)
    assert "URL" in result.unresolved_keys
    assert not result.is_clean


def test_external_fills_missing_ref():
    env = {"FULL_URL": "${SCHEME}://localhost"}
    result = interpolate_env(env, external={"SCHEME": "https"})
    assert result.resolved["FULL_URL"] == "https://localhost"
    assert result.is_clean


def test_cycle_detected():
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate_env(env)
    assert set(result.cycle_keys) == {"A", "B"} or len(result.cycle_keys) >= 1
    assert not result.is_clean


def test_chain_resolution():
    env = {"A": "foo", "B": "${A}bar", "C": "${B}baz"}
    result = interpolate_env(env)
    assert result.resolved["C"] == "foobarbaz"


def test_summary_all_resolved(simple_env):
    result = interpolate_env(simple_env)
    assert "resolved" in result.summary
    assert "unresolved" not in result.summary


def test_summary_mentions_unresolved():
    env = {"X": "${MISSING}"}
    result = interpolate_env(env)
    assert "unresolved" in result.summary


# --- formatter tests ---

def test_format_includes_header(simple_env):
    result = interpolate_env(simple_env)
    output = format_interpolate(result)
    assert "Interpolation Report" in output


def test_format_shows_ok_when_clean(simple_env):
    result = interpolate_env(simple_env)
    output = format_interpolate(result, color=False)
    assert "OK" in output


def test_format_shows_unresolved_label():
    env = {"X": "${MISSING}"}
    result = interpolate_env(env)
    output = format_interpolate(result, color=False)
    assert "UNRESOLVED" in output
    assert "X" in output


def test_format_shows_cycle_label():
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate_env(env)
    output = format_interpolate(result, color=False)
    assert "CYCLE" in output
