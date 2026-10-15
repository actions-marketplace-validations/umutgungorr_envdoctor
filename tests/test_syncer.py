"""Tests for template synchronization logic."""

from pathlib import Path

import pytest

from envdoctor.parser import parse_env_text
from envdoctor.syncer import generate_safe_placeholder, sync_example_file


def test_safe_placeholder_generation() -> None:
    assert generate_safe_placeholder("PORT") == "8080"
    assert generate_safe_placeholder("SERVER_PORT") == "8080"
    assert "postgresql://" in generate_safe_placeholder("DATABASE_URL")
    assert generate_safe_placeholder("DB_HOST") == "localhost"
    assert generate_safe_placeholder("STRIPE_SECRET_KEY") == "your_stripe_secret_key_here"
    assert generate_safe_placeholder("DEBUG") == "true"
    assert generate_safe_placeholder("USER_EMAIL") == "user@example.com"


def test_sync_appends_missing_keys_to_example(tmp_path: Path) -> None:
    example_file = tmp_path / ".env.example"
    example_file.write_text("PORT=3000\n", encoding="utf-8")

    env_map = parse_env_text(
        "PORT=8080\nSTRIPE_API_KEY=sk_live_123456\nDATABASE_URL=postgres://...\n"
    )

    res = sync_example_file(env_map, example_file, dry_run=False)

    assert res.was_written is True
    assert "STRIPE_API_KEY" in res.added_keys
    assert "DATABASE_URL" in res.added_keys
    assert "PORT" in res.skipped_keys

    updated_content = example_file.read_text(encoding="utf-8")
    assert "STRIPE_API_KEY=your_stripe_api_key_here" in updated_content
    # Real secret must NEVER be written to .env.example
    assert "sk_live_123456" not in updated_content


def test_sync_dry_run_does_not_modify_file(tmp_path: Path) -> None:
    example_file = tmp_path / ".env.example"
    initial_text = "PORT=3000\n"
    example_file.write_text(initial_text, encoding="utf-8")

    env_map = parse_env_text("PORT=3000\nNEW_KEY=val\n")

    res = sync_example_file(env_map, example_file, dry_run=True)
    assert res.was_written is False
    assert len(res.added_keys) == 1
    assert example_file.read_text(encoding="utf-8") == initial_text


@pytest.mark.parametrize("dry_run", [False, True])
def test_sync_never_exports_private_inline_comments(tmp_path, dry_run):
    example = tmp_path / ".env.example"
    example.write_text("PORT=3000\n", encoding="utf-8")
    env_map = parse_env_text("TOKEN=private-value # private-comment-marker\n")
    result = sync_example_file(env_map, example, dry_run=dry_run)
    output = "\n".join(result.output_lines) + example.read_text(encoding="utf-8")
    assert "TOKEN=your_token_here" in output
    assert "private-value" not in output
    assert "private-comment-marker" not in output


def test_unreadable_existing_template_is_not_replaced(tmp_path, monkeypatch):
    example = tmp_path / ".env.example"
    original = b"# Preserve this\nPORT=3000\n"
    example.write_bytes(original)
    read_text = Path.read_text

    def fail_for_template(path, *args, **kwargs):
        if path == example:
            raise PermissionError("Synthetic read failure")
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_for_template)
    with pytest.raises(PermissionError):
        sync_example_file(parse_env_text("NEW_KEY=value\n"), example)
    assert example.read_bytes() == original
