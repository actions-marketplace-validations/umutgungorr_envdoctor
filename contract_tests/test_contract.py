import os
import subprocess
import sys
from pathlib import Path

from envdoctor.main import build_parser


def test_cli_help() -> None:
    parser = build_parser()
    assert parser.prog == "envdoctor"


def test_cli_invoked_via_module() -> None:
    src_dir = str(Path(__file__).resolve().parent.parent / "src")
    env = dict(os.environ, PYTHONPATH=src_dir)
    proc = subprocess.run(
        [sys.executable, "-m", "envdoctor", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0
    assert "envdoctor" in proc.stdout.lower()
