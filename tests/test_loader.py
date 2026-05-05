"""Tests for envcast.loader module."""

import os
import pytest
from pathlib import Path

from envcast.loader import EnvLoader


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    content = (
        "# Sample env file\n"
        "APP_ENV=production\n"
        "DB_HOST=localhost\n"
        'DB_PASSWORD="secret123"\n'
        "DEBUG=false\n"
    )
    env_path = tmp_path / ".env"
    env_path.write_text(content)
    return env_path


def test_load_file_parses_key_value_pairs(env_file):
    loader = EnvLoader(str(env_file))
    env = loader.load_file()
    assert env["APP_ENV"] == "production"
    assert env["DB_HOST"] == "localhost"
    assert env["DEBUG"] == "false"


def test_load_file_strips_quotes(env_file):
    loader = EnvLoader(str(env_file))
    env = loader.load_file()
    assert env["DB_PASSWORD"] == "secret123"


def test_load_file_ignores_comments_and_blanks(env_file):
    loader = EnvLoader(str(env_file))
    env = loader.load_file()
    assert len(env) == 4


def test_load_file_raises_if_missing():
    loader = EnvLoader("/nonexistent/.env")
    with pytest.raises(FileNotFoundError):
        loader.load_file()


def test_load_file_raises_on_invalid_format(tmp_path):
    bad_env = tmp_path / ".env"
    bad_env.write_text("INVALID_LINE_NO_EQUALS\n")
    loader = EnvLoader(str(bad_env))
    with pytest.raises(ValueError, match="Invalid format"):
        loader.load_file()


def test_load_system_returns_env_vars():
    loader = EnvLoader()
    env = loader.load_system()
    assert isinstance(env, dict)
    assert len(env) > 0


def test_load_system_with_prefix():
    os.environ["ENVCAST_TEST_VAR"] = "hello"
    loader = EnvLoader()
    env = loader.load_system(prefix="ENVCAST_")
    assert "ENVCAST_TEST_VAR" in env
    assert all(k.startswith("ENVCAST_") for k in env)


def test_env_property_returns_copy(env_file):
    loader = EnvLoader(str(env_file))
    loader.load_file()
    env_copy = loader.env
    env_copy["NEW_KEY"] = "should_not_persist"
    assert "NEW_KEY" not in loader.env
