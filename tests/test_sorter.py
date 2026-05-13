"""Tests for envcast.sorter and envcast.sort_formatter."""

import pytest

from envcast.sorter import sort_env, SortResult
from envcast.sort_formatter import format_sort


@pytest.fixture()
def sample_env():
    return {
        "ZEBRA": "1",
        "APP_NAME": "envcast",
        "DB_HOST": "localhost",
        "API_KEY": "secret",
        "PORT": "8080",
    }


# ---------------------------------------------------------------------------
# sort_env — alpha
# ---------------------------------------------------------------------------

def test_alpha_sort_order(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    assert result.sorted_order == sorted(sample_env.keys(), key=str.casefold)


def test_alpha_sort_strategy_label(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    assert result.strategy == "alpha"


def test_alpha_sorted_env_contains_all_keys(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    assert set(result.sorted_env.keys()) == set(sample_env.keys())


def test_alpha_desc_sort_order(sample_env):
    result = sort_env(sample_env, strategy="alpha_desc")
    assert result.sorted_order == sorted(sample_env.keys(), key=str.casefold, reverse=True)


def test_length_sort_shortest_first(sample_env):
    result = sort_env(sample_env, strategy="length")
    lengths = [len(k) for k in result.sorted_order]
    assert lengths == sorted(lengths)


# ---------------------------------------------------------------------------
# sort_env — grouped
# ---------------------------------------------------------------------------

def test_grouped_sort_prefixed_keys_come_first(sample_env):
    result = sort_env(sample_env, strategy="grouped", groups=["DB_", "API_"])
    grouped = [k for k in result.sorted_order if k.startswith(("DB_", "API_"))]
    rest = [k for k in result.sorted_order if not k.startswith(("DB_", "API_"))]
    assert result.sorted_order == grouped + rest


def test_grouped_sort_without_groups_falls_back_to_alpha(sample_env):
    result = sort_env(sample_env, strategy="grouped", groups=[])
    assert result.sorted_order == sorted(sample_env.keys(), key=str.casefold)


# ---------------------------------------------------------------------------
# sort_env — edge cases
# ---------------------------------------------------------------------------

def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort_env({"A": "1"}, strategy="bogus")


def test_already_sorted_detects_no_change():
    env = {"ALPHA": "1", "BETA": "2", "GAMMA": "3"}
    result = sort_env(env, strategy="alpha")
    assert not result.order_changed


def test_order_changed_when_reordered(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    # sample_env starts with ZEBRA which will move — order must change
    assert result.order_changed


def test_key_count_matches_input(sample_env):
    result = sort_env(sample_env)
    assert result.key_count == len(sample_env)


# ---------------------------------------------------------------------------
# format_sort
# ---------------------------------------------------------------------------

def test_format_includes_strategy_header(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    output = format_sort(result)
    assert "alpha" in output


def test_format_shows_no_change_message_when_sorted():
    env = {"ALPHA": "1", "BETA": "2"}
    result = sort_env(env, strategy="alpha")
    output = format_sort(result)
    assert "Already in sorted order" in output


def test_format_shows_moved_indicator_when_changed(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    output = format_sort(result)
    # The ↕ arrow should appear for at least one moved key
    assert "↕" in output


def test_format_includes_key_count(sample_env):
    result = sort_env(sample_env)
    output = format_sort(result)
    assert str(result.key_count) in output
