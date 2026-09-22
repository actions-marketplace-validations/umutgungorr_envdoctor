"""Tests for .env comparison and diff logic."""

from envdoctor.differ import compare_environments, format_diff_report
from envdoctor.parser import parse_env_text


def test_clean_match_passes() -> None:
    env_content = "PORT=8080\nSECRET=supersecret\n"
    example_content = "PORT=3000\nSECRET=your_secret\n"

    diff = compare_environments(
        parse_env_text(env_content),
        parse_env_text(example_content),
    )
    assert diff.is_clean is True
    assert diff.is_strict_clean() is True
    assert len(diff.missing_in_env) == 0
    assert len(diff.missing_in_example) == 0


def test_detects_missing_in_env() -> None:
    env_content = "PORT=8080\n"
    example_content = "PORT=8080\nDATABASE_URL=postgres://...\nREDIS_HOST=localhost\n"

    diff = compare_environments(
        parse_env_text(env_content),
        parse_env_text(example_content),
    )
    assert diff.is_clean is False
    assert diff.missing_in_env == ["DATABASE_URL", "REDIS_HOST"]


def test_detects_missing_in_example() -> None:
    env_content = "PORT=8080\nNEW_FEATURE_FLAG=true\n"
    example_content = "PORT=8080\n"

    diff = compare_environments(
        parse_env_text(env_content),
        parse_env_text(example_content),
    )
    assert diff.is_clean is True  # still clean in standard mode because no required key is missing
    assert diff.is_strict_clean() is False
    assert diff.missing_in_example == ["NEW_FEATURE_FLAG"]


def test_detects_empty_variables() -> None:
    env_content = "PORT=8080\nAPI_KEY=\n"
    example_content = "PORT=8080\nAPI_KEY=your_key\n"

    diff = compare_environments(
        parse_env_text(env_content),
        parse_env_text(example_content),
    )
    assert diff.empty_in_env == ["API_KEY"]


def test_diff_report_formatting() -> None:
    env_content = "PORT=8080\n"
    example_content = "PORT=8080\nDB_PASS=secret\n"

    diff = compare_environments(
        parse_env_text(env_content),
        parse_env_text(example_content),
    )
    report = format_diff_report(diff)
    assert "EnvDoctor Health Check Report" in report
    assert "DB_PASS" in report
    assert "CRITICAL" in report
