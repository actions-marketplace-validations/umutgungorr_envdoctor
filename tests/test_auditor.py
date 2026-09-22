"""Tests for codebase auditor logic."""

from pathlib import Path

from envdoctor.auditor import audit_codebase, scan_file_for_env_keys


def test_scans_python_file(tmp_path: Path) -> None:
    code = """
import os

db_url = os.environ["DATABASE_URL"]
port = os.getenv("PORT")
secret = os.environ.get("JWT_SECRET")
"""
    py_file = tmp_path / "app.py"
    py_file.write_text(code, encoding="utf-8")

    refs = scan_file_for_env_keys(py_file)
    found_keys = {r.key for r in refs}
    assert found_keys == {"DATABASE_URL", "PORT", "JWT_SECRET"}


def test_scans_javascript_file(tmp_path: Path) -> None:
    code = """
const port = process.env.PORT || 3000;
const apiKey = process.env["STRIPE_KEY"];
"""
    js_file = tmp_path / "server.js"
    js_file.write_text(code, encoding="utf-8")

    refs = scan_file_for_env_keys(js_file)
    found_keys = {r.key for r in refs}
    assert found_keys == {"PORT", "STRIPE_KEY"}


def test_audit_reports_missing_and_stale(tmp_path: Path) -> None:
    py_file = tmp_path / "main.py"
    py_file.write_text("import os\nurl = os.getenv('PAYMENT_GATEWAY_URL')\n", encoding="utf-8")

    known_envs = {"UNUSED_OLD_VAR", "ANOTHER_UNUSED"}

    res = audit_codebase([tmp_path], known_envs)
    assert "PAYMENT_GATEWAY_URL" in res.missing_from_env
    assert "UNUSED_OLD_VAR" in res.stale_in_env
