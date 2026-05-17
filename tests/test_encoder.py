"""Tests for envcast.encoder."""
import base64
import urllib.parse

import pytest

from envcast.encoder import EncodeEntry, EncodeResult, encode_env


@pytest.fixture
def sample_env():
    return {
        "DB_PASSWORD": "s3cr3t!",
        "APP_NAME": "envcast",
        "PORT": "8080",
    }


def test_encode_returns_encode_result(sample_env):
    result = encode_env(sample_env)
    assert isinstance(result, EncodeResult)


def test_encode_entry_count_matches_env(sample_env):
    result = encode_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_base64_encoding_correct(sample_env):
    result = encode_env(sample_env, encoding="base64")
    for entry in result.entries:
        expected = base64.b64encode(entry.original.encode()).decode()
        assert entry.encoded == expected


def test_url_encoding_correct(sample_env):
    result = encode_env(sample_env, encoding="url")
    for entry in result.entries:
        expected = urllib.parse.quote(entry.original, safe="")
        assert entry.encoded == expected


def test_hex_encoding_correct(sample_env):
    result = encode_env(sample_env, encoding="hex")
    for entry in result.entries:
        expected = entry.original.encode().hex()
        assert entry.encoded == expected


def test_changed_count_all_keys(sample_env):
    result = encode_env(sample_env, encoding="base64")
    # All values differ from their base64 form (none are already base64-encoded)
    assert result.changed_count() == len(sample_env)
    assert result.has_changes()


def test_selective_keys_only_encodes_specified(sample_env):
    result = encode_env(sample_env, encoding="base64", keys=["DB_PASSWORD"])
    encoded_entries = [e for e in result.entries if e.changed]
    assert len(encoded_entries) == 1
    assert encoded_entries[0].key == "DB_PASSWORD"


def test_unselected_keys_pass_through_unchanged(sample_env):
    result = encode_env(sample_env, encoding="base64", keys=["DB_PASSWORD"])
    unchanged = {e.key: e.encoded for e in result.entries if not e.changed}
    assert unchanged["APP_NAME"] == sample_env["APP_NAME"]
    assert unchanged["PORT"] == sample_env["PORT"]


def test_to_env_returns_dict(sample_env):
    result = encode_env(sample_env, encoding="hex")
    env_dict = result.to_env()
    assert isinstance(env_dict, dict)
    assert set(env_dict.keys()) == set(sample_env.keys())


def test_unknown_encoding_raises():
    with pytest.raises(ValueError, match="Unknown encoding"):
        encode_env({"KEY": "value"}, encoding="rot13")  # type: ignore[arg-type]


def test_empty_env_produces_no_entries():
    result = encode_env({}, encoding="base64")
    assert len(result.entries) == 0
    assert not result.has_changes()


def test_encoding_label_stored_on_entry(sample_env):
    result = encode_env(sample_env, encoding="url")
    for entry in result.entries:
        assert entry.encoding == "url"
