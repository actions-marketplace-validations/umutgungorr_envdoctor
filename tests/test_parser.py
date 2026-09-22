"""Tests for .env file parser."""

from pathlib import Path

from envdoctor.parser import parse_env_file, parse_env_text


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


def test_parses_multiline_and_escaped_quotes() -> None:
    content = (
        'MULTILINE="first line\nsecond line\nthird line"\n'
        'ESCAPED="hello \\"world\\""\n'
        "SINGLE_ESCAPED='it\\'s fine'\n"
    )
    entries = parse_env_text(content)
    assert entries["MULTILINE"].value == "first line\nsecond line\nthird line"
    assert entries["ESCAPED"].value == 'hello "world"'
    assert entries["SINGLE_ESCAPED"].value == "it's fine"


def test_parses_fixture_file() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "complex.env"
    entries = parse_env_file(fixture_path)
    assert len(entries) >= 6
    assert entries["PORT"].value == "3000"
    assert entries["DB_PORT"].is_exported is True
    assert "BEGIN CERTIFICATE" in entries["TLS_CERT"].value
    assert entries["CUSTOM_GREETING"].value == 'Hello "World"'
    assert entries["API_SECRET"].value == "secret'with'quotes"
    assert entries["EMPTY_KEY"].value == ""
