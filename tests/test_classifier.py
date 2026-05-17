"""Tests for envcast.classifier."""
import pytest
from envcast.classifier import (
    classify_env,
    ClassifyResult,
    ClassifyEntry,
    UNCLASSIFIED,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "AWS_REGION": "us-east-1",
        "AWS_SECRET_KEY": "abc123",
        "SMTP_HOST": "mail.example.com",
        "LOG_LEVEL": "INFO",
        "FEATURE_DARK_MODE": "true",
        "APP_PORT": "8080",
        "RANDOM_SETTING": "foo",
    }


def test_classify_returns_classify_result(sample_env):
    result = classify_env(sample_env)
    assert isinstance(result, ClassifyResult)


def test_classify_entry_count_matches_env(sample_env):
    result = classify_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_classify_entry_type(sample_env):
    result = classify_env(sample_env)
    for entry in result.entries:
        assert isinstance(entry, ClassifyEntry)


def test_db_host_classified_as_database(sample_env):
    result = classify_env(sample_env)
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.category == "database"


def test_aws_region_classified_as_cloud(sample_env):
    result = classify_env(sample_env)
    entry = next(e for e in result.entries if e.key == "AWS_REGION")
    assert entry.category == "cloud"


def test_smtp_host_classified_as_email(sample_env):
    result = classify_env(sample_env)
    entry = next(e for e in result.entries if e.key == "SMTP_HOST")
    assert entry.category == "email"


def test_log_level_classified_as_logging(sample_env):
    result = classify_env(sample_env)
    entry = next(e for e in result.entries if e.key == "LOG_LEVEL")
    assert entry.category == "logging"


def test_feature_flag_classified_as_feature(sample_env):
    result = classify_env(sample_env)
    entry = next(e for e in result.entries if e.key == "FEATURE_DARK_MODE")
    assert entry.category == "feature"


def test_unknown_key_classified_as_unclassified():
    result = classify_env({"RANDOM_SETTING": "foo"})
    assert result.entries[0].category == UNCLASSIFIED


def test_has_unclassified_true_when_unknown_present(sample_env):
    result = classify_env(sample_env)
    assert result.has_unclassified()


def test_has_unclassified_false_when_all_known():
    env = {"DB_HOST": "localhost", "AWS_REGION": "us-east-1"}
    result = classify_env(env)
    assert not result.has_unclassified()


def test_keys_in_category_returns_correct_keys(sample_env):
    result = classify_env(sample_env)
    db_keys = result.keys_in_category("database")
    assert "DB_HOST" in db_keys
    assert "DB_PASSWORD" in db_keys


def test_category_count_reflects_distinct_categories(sample_env):
    result = classify_env(sample_env)
    assert result.category_count() == len(result.categories())


def test_empty_env_returns_empty_result():
    result = classify_env({})
    assert len(result.entries) == 0
    assert result.category_count() == 0
    assert not result.has_unclassified()
