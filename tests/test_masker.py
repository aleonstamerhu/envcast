"""Tests for envcast.masker."""
import pytest
from envcast.masker import mask_env, DEFAULT_MASK, MaskResult


@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t!",
        "API_KEY": "abcdef123456",
        "AUTH_TOKEN": "tok_live_xyz",
        "DEBUG": "true",
        "EMPTY_SECRET": "",
    }


def test_mask_result_is_mask_result_type(sample_env):
    result = mask_env(sample_env)
    assert isinstance(result, MaskResult)


def test_non_sensitive_keys_unchanged(sample_env):
    result = mask_env(sample_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_password_key_is_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK


def test_api_key_is_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["API_KEY"] == DEFAULT_MASK


def test_token_key_is_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["AUTH_TOKEN"] == DEFAULT_MASK


def test_empty_sensitive_value_stays_empty(sample_env):
    result = mask_env(sample_env)
    assert result.masked["EMPTY_SECRET"] == ""


def test_masked_keys_list_sorted(sample_env):
    result = mask_env(sample_env)
    assert result.masked_keys == sorted(result.masked_keys)


def test_masked_count_matches_list(sample_env):
    result = mask_env(sample_env)
    assert result.masked_count == len(result.masked_keys)


def test_has_masked_true_when_sensitive_present(sample_env):
    result = mask_env(sample_env)
    assert result.has_masked is True


def test_has_masked_false_for_clean_env():
    result = mask_env({"HOST": "localhost", "PORT": "5432"})
    assert result.has_masked is False


def test_original_env_preserved(sample_env):
    result = mask_env(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t!"


def test_extra_keys_treated_as_sensitive(sample_env):
    result = mask_env(sample_env, extra_keys=["APP_NAME"])
    assert result.masked["APP_NAME"] == DEFAULT_MASK
    assert "APP_NAME" in result.masked_keys


def test_partial_mode_reveals_edges():
    env = {"API_KEY": "abcdefghijklmnop"}
    result = mask_env(env, partial=True)
    val = result.masked["API_KEY"]
    assert val.startswith("abcd")
    assert val.endswith("mnop")
    assert "****" in val


def test_partial_mode_short_value_fully_masked():
    env = {"DB_PASSWORD": "short"}
    result = mask_env(env, partial=True)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
