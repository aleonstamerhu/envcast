"""Tests for envcast.rotator."""
import pytest

from envcast.rotator import RotateEntry, RotateResult, rotate_env


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD_OLD": "secret",
        "OLD_API_KEY": "abc123",
        "LEGACY_TOKEN": "tok",
        "APP_SECRET_V1": "v1secret",
        "CLEAN_KEY": "value",
    }


def test_rotate_returns_rotate_result(sample_env):
    result = rotate_env(sample_env)
    assert isinstance(result, RotateResult)


def test_rotate_entry_count_matches_env(sample_env):
    result = rotate_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_rotate_detects_old_suffix(sample_env):
    result = rotate_env(sample_env)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD_OLD")
    assert entry.suggested_key == "DB_PASSWORD"
    assert "_OLD" in entry.reason


def test_rotate_detects_old_prefix(sample_env):
    result = rotate_env(sample_env)
    entry = next(e for e in result.entries if e.key == "OLD_API_KEY")
    assert entry.suggested_key == "API_KEY"
    assert "OLD_" in entry.reason


def test_rotate_detects_legacy_prefix(sample_env):
    result = rotate_env(sample_env)
    entry = next(e for e in result.entries if e.key == "LEGACY_TOKEN")
    assert entry.suggested_key == "TOKEN"


def test_rotate_detects_v1_suffix(sample_env):
    result = rotate_env(sample_env)
    entry = next(e for e in result.entries if e.key == "APP_SECRET_V1")
    assert entry.suggested_key == "APP_SECRET"


def test_clean_key_has_no_suggestion(sample_env):
    result = rotate_env(sample_env)
    entry = next(e for e in result.entries if e.key == "CLEAN_KEY")
    assert entry.suggested_key is None
    assert entry.reason is None


def test_has_rotations_false_without_apply(sample_env):
    result = rotate_env(sample_env, apply=False)
    assert result.has_rotations is False


def test_has_rotations_true_with_apply(sample_env):
    result = rotate_env(sample_env, apply=True)
    assert result.has_rotations is True


def test_rotated_count_with_apply(sample_env):
    result = rotate_env(sample_env, apply=True)
    # DB_PASSWORD_OLD, OLD_API_KEY, LEGACY_TOKEN, APP_SECRET_V1 → 4 stale keys
    assert result.rotated_count == 4


def test_rotated_env_contains_new_keys(sample_env):
    result = rotate_env(sample_env, apply=True)
    env = result.rotated_env
    assert "DB_PASSWORD" in env
    assert "API_KEY" in env
    assert "TOKEN" in env
    assert "APP_SECRET" in env


def test_rotated_env_excludes_old_keys_when_applied(sample_env):
    result = rotate_env(sample_env, apply=True)
    env = result.rotated_env
    assert "DB_PASSWORD_OLD" not in env
    assert "OLD_API_KEY" not in env


def test_rotated_env_preserves_clean_keys(sample_env):
    result = rotate_env(sample_env, apply=True)
    assert result.rotated_env["DB_HOST"] == "localhost"
    assert result.rotated_env["CLEAN_KEY"] == "value"


def test_custom_mapping_overrides_auto_detection():
    env = {"MYKEY": "val", "OTHER": "x"}
    result = rotate_env(env, apply=True, custom_mapping={"MYKEY": "MY_KEY_NEW"})
    assert result.rotated_env["MY_KEY_NEW"] == "val"
    assert "MYKEY" not in result.rotated_env


def test_keys_with_suggestions_returns_only_flagged(sample_env):
    result = rotate_env(sample_env)
    flagged = result.keys_with_suggestions()
    keys = [e.key for e in flagged]
    assert "DB_PASSWORD_OLD" in keys
    assert "CLEAN_KEY" not in keys
    assert "DB_HOST" not in keys
