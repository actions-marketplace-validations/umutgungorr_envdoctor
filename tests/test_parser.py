"""Tests for .env file parser."""

from envdoctor.parser import parse_env_text


def test_parses_simple_key_values() -> None:
    content = "PORT=8080\nHOST=localhost\nDEBUG=true\n"
    entries = parse_env_text(content)
    assert len(entries) == 3
    assert entries["PORT"].value == "8080"
    assert entries["HOST"].value == "localhost"
    assert entries["DEBUG"].value == "true"


def test_parses_export_prefix() -> None:
    content = "export DATABASE_URL=postgres://localhost:5432/app\nexport API_KEY=xyz123"
    entries = parse_env_text(content)
    assert len(entries) == 2
    assert entries["DATABASE_URL"].is_exported is True
    assert entries["DATABASE_URL"].value == "postgres://localhost:5432/app"
    assert entries["API_KEY"].is_exported is True


def test_parses_quoted_values_and_inline_comments() -> None:
    content = (
        'APP_NAME="My Project #1" # Title of app\n'
        "TOKEN='secret_token#raw'\n"
        "CACHE_DIR=/tmp/cache # temp folder\n"
    )
    entries = parse_env_text(content)
    assert entries["APP_NAME"].value == "My Project #1"
    assert entries["APP_NAME"].comment == "Title of app"
    assert entries["TOKEN"].value == "secret_token#raw"
    assert entries["CACHE_DIR"].value == "/tmp/cache"
    assert entries["CACHE_DIR"].comment == "temp folder"


def test_parses_empty_values() -> None:
    content = "OPTIONAL_KEY=\nEMPTY_QUOTED=\"\"\n"
    entries = parse_env_text(content)
    assert entries["OPTIONAL_KEY"].value == ""
    assert entries["EMPTY_QUOTED"].value == ""


def test_ignores_comments_and_empty_lines() -> None:
    content = """
    # This is a full line comment
    # Another comment

    APP_ENV=production

    # Footer comment
    """
    entries = parse_env_text(content)
    assert len(entries) == 1
    assert "APP_ENV" in entries
    assert entries["APP_ENV"].value == "production"
