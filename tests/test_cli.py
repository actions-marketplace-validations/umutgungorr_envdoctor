"""End-to-end tests for EnvDoctor CLI execution."""

from pathlib import Path

from envdoctor.main import build_parser, main


def test_cli_help() -> None:
    parser = build_parser()
    assert parser.prog == "envdoctor"


def test_cli_check_success(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    env_file.write_text("PORT=8080\nSECRET=123\n", encoding="utf-8")
    example_file.write_text("PORT=3000\nSECRET=xyz\n", encoding="utf-8")

    exit_code = main(["check", "--env", str(env_file), "--example", str(example_file)])
    assert exit_code == 0


def test_cli_check_missing_fails(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    env_file.write_text("PORT=8080\n", encoding="utf-8")
    example_file.write_text("PORT=3000\nREQUIRED_VAR=needs_setting\n", encoding="utf-8")

    exit_code = main(["check", "--env", str(env_file), "--example", str(example_file)])
    assert exit_code == 1


def test_cli_sync_command(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    env_file.write_text("PORT=8080\nNEW_KEY=val\n", encoding="utf-8")
    example_file.write_text("PORT=3000\n", encoding="utf-8")

    exit_code = main(["sync", "--env", str(env_file), "--example", str(example_file)])
    assert exit_code == 0
    assert "NEW_KEY" in example_file.read_text(encoding="utf-8")


def test_cli_audit_command(tmp_path: Path) -> None:
    code_file = tmp_path / "app.py"
    code_file.write_text("import os\nval = os.getenv('CONFIG_PATH')\n", encoding="utf-8")

    env_file = tmp_path / ".env"
    env_file.write_text("CONFIG_PATH=/etc/app\n", encoding="utf-8")

    exit_code = main(["audit", str(tmp_path), "--env", str(env_file)])
    assert exit_code == 0
