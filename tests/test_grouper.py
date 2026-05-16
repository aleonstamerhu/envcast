"""Tests for envcast.grouper."""
import pytest
from envcast.grouper import GroupEntry, GroupResult, group_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_group_env_returns_group_result(sample_env):
    result = group_env(sample_env)
    assert isinstance(result, GroupResult)


def test_group_env_entry_count_matches_env(sample_env):
    result = group_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_auto_prefix_groups_db_keys(sample_env):
    result = group_env(sample_env)
    assert "DB" in result.group_names()
    assert set(result.keys_in_group("DB")) == {"DB_HOST", "DB_PORT"}


def test_auto_prefix_groups_aws_keys(sample_env):
    result = group_env(sample_env)
    assert "AWS" in result.group_names()
    assert set(result.keys_in_group("AWS")) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_keys_without_separator_go_to_ungrouped(sample_env):
    result = group_env(sample_env)
    ungrouped_keys = {e.key for e in result.ungrouped()}
    assert "DEBUG" in ungrouped_keys
    assert "PORT" in ungrouped_keys


def test_group_count_reflects_distinct_groups(sample_env):
    result = group_env(sample_env)
    # DB, AWS, (ungrouped)
    assert result.group_count() == 3


def test_explicit_prefix_map_overrides_auto(sample_env):
    prefix_map = {"DB": "Database", "AWS": "Cloud"}
    result = group_env(sample_env, prefix_map=prefix_map)
    assert "Database" in result.group_names()
    assert "Cloud" in result.group_names()
    assert "DB" not in result.group_names()
    assert "AWS" not in result.group_names()


def test_explicit_prefix_map_assigns_correct_keys(sample_env):
    prefix_map = {"DB": "Database"}
    result = group_env(sample_env, prefix_map=prefix_map)
    assert set(result.keys_in_group("Database")) == {"DB_HOST", "DB_PORT"}


def test_entry_has_correct_group_label(sample_env):
    result = group_env(sample_env)
    db_entries = [e for e in result.entries if e.key.startswith("DB_")]
    assert all(e.group == "DB" for e in db_entries)


def test_entry_preserves_value(sample_env):
    result = group_env(sample_env)
    entry_map = {e.key: e for e in result.entries}
    assert entry_map["DB_HOST"].value == "localhost"
    assert entry_map["AWS_ACCESS_KEY"].value == "AKIA123"


def test_group_names_sorted(sample_env):
    result = group_env(sample_env)
    names = result.group_names()
    assert names == sorted(names)


def test_empty_env_produces_empty_result():
    result = group_env({})
    assert result.entries == []
    assert result.group_count() == 0
    assert result.group_names() == []


def test_custom_separator():
    env = {"APP.HOST": "localhost", "APP.PORT": "80", "STANDALONE": "yes"}
    result = group_env(env, separator=".")
    assert "APP" in result.group_names()
    assert set(result.keys_in_group("APP")) == {"APP.HOST", "APP.PORT"}
