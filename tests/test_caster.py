"""Tests for envcast.caster."""
import pytest
from envcast.caster import CastEntry, CastResult, cast_env, _infer_type, _cast


@pytest.fixture
def sample_env():
    return {
        "DEBUG": "true",
        "PORT": "8080",
        "RATIO": "3.14",
        "APP_NAME": "myapp",
        "RETRIES": "0",
        "VERBOSE": "yes",
        "TIMEOUT": "30.0",
    }


# --- _infer_type ---

def test_infer_bool_true():
    assert _infer_type("true") == "bool"

def test_infer_bool_false():
    assert _infer_type("false") == "bool"

def test_infer_bool_yes():
    assert _infer_type("yes") == "bool"

def test_infer_int():
    assert _infer_type("42") == "int"

def test_infer_float():
    assert _infer_type("3.14") == "float"

def test_infer_str():
    assert _infer_type("hello") == "str"


# --- cast_env ---

def test_cast_returns_cast_result(sample_env):
    result = cast_env(sample_env)
    assert isinstance(result, CastResult)

def test_cast_entry_count_matches_env(sample_env):
    result = cast_env(sample_env)
    assert len(result.entries) == len(sample_env)

def test_cast_bool_true(sample_env):
    result = cast_env(sample_env)
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.cast_value is True
    assert entry.type_label == "bool"

def test_cast_bool_zero():
    result = cast_env({"FLAG": "0"})
    entry = result.entries[0]
    assert entry.cast_value is False

def test_cast_int(sample_env):
    result = cast_env(sample_env)
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.cast_value == 8080
    assert entry.type_label == "int"

def test_cast_float(sample_env):
    result = cast_env(sample_env)
    entry = next(e for e in result.entries if e.key == "RATIO")
    assert abs(entry.cast_value - 3.14) < 1e-9
    assert entry.type_label == "float"

def test_cast_str(sample_env):
    result = cast_env(sample_env)
    entry = next(e for e in result.entries if e.key == "APP_NAME")
    assert entry.cast_value == "myapp"
    assert entry.type_label == "str"

def test_cast_type_map_override():
    env = {"PORT": "8080"}
    result = cast_env(env, type_map={"PORT": "str"})
    entry = result.entries[0]
    assert entry.cast_value == "8080"
    assert entry.type_label == "str"

def test_cast_failure_marks_entry():
    env = {"PORT": "not-a-number"}
    result = cast_env(env, type_map={"PORT": "int"})
    entry = result.entries[0]
    assert entry.failed is True
    assert result.has_failures is True
    assert result.failed_count == 1

def test_cast_as_dict_excludes_failures():
    env = {"PORT": "bad", "DEBUG": "true"}
    result = cast_env(env, type_map={"PORT": "int"})
    d = result.as_dict()
    assert "PORT" not in d
    assert d["DEBUG"] is True

def test_no_failures_has_failures_false(sample_env):
    result = cast_env(sample_env)
    assert result.has_failures is False
    assert result.failed_count == 0
