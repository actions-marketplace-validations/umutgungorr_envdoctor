"""Codebase auditor: scans application source code for environment variable usages."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

AUDIT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".php",
    ".rb",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}

# High-precision patterns for extracting env variables from source code
PATTERNS = [
    # Python: os.environ["KEY"], os.environ.get("KEY"), os.getenv("KEY")
    re.compile(r"""(?:os\.environ(?:\[|\.get\()|os\.getenv\()\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
    # JS/TS: process.env.KEY or process.env["KEY"]
    re.compile(r"""process\.env\.([A-Za-z_][A-Za-z0-9_]*)|process\.env\[\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*\]"""),
    # Go: os.Getenv("KEY")
    re.compile(r"""os\.Getenv\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
    # Rust: env::var("KEY")
    re.compile(r"""env::var\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""),
]


@dataclass(slots=True)
class CodeReference:
    key: str
    file_path: str
    line_number: int
    line_snippet: str


@dataclass(slots=True)
class AuditResult:
    references: list[CodeReference]
    unique_referenced_keys: set[str]
    missing_from_env: set[str]
    stale_in_env: set[str]


def scan_file_for_env_keys(file_path: Path) -> list[CodeReference]:
    """Scan a single source file for environment variable lookups."""
    if file_path.suffix.lower() not in AUDIT_EXTENSIONS:
        return []

    references: list[CodeReference] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "#", "/*", "*")):
            continue

        for pat in PATTERNS:
            for match in pat.finditer(line):
                # pattern 2 has two capture groups
                key = match.group(1) or (match.group(2) if len(match.groups()) > 1 else None)
                if key and len(key) >= 2:
                    references.append(
                        CodeReference(
                            key=key,
                            file_path=str(file_path),
                            line_number=idx,
                            line_snippet=stripped[:80],
                        )
                    )
    return references


def audit_codebase(
    target_paths: Iterable[Path],
    known_env_keys: set[str],
) -> AuditResult:
    """Scan all files under target paths and compare detected env keys with known .env keys."""
    all_refs: list[CodeReference] = []

    for target in target_paths:
        if target.is_file():
            all_refs.extend(scan_file_for_env_keys(target))
        elif target.is_dir():
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                for file in files:
                    p = Path(root) / file
                    all_refs.extend(scan_file_for_env_keys(p))

    referenced_keys = {ref.key for ref in all_refs}
    missing_from_env = referenced_keys - known_env_keys
    stale_in_env = known_env_keys - referenced_keys

    return AuditResult(
        references=all_refs,
        unique_referenced_keys=referenced_keys,
        missing_from_env=missing_from_env,
        stale_in_env=stale_in_env,
    )
