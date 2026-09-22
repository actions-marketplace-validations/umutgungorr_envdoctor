"""Parser implementation for .env and .env.example files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class EnvEntry:
    key: str
    value: str
    line_number: int
    raw_line: str
    comment: str | None = None
    is_exported: bool = False


# Matches key assignment: optional 'export ', key name, '=', optional rest
KEY_ASSIGN_PATTERN = re.compile(
    r"^(?P<export>export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<rest>.*)$"
)


def _parse_value_and_comment(raw_val: str) -> tuple[str, str | None]:
    """Extract actual value and optional inline comment from the right-hand side of '='."""
    stripped = raw_val.strip()
    if not stripped:
        return "", None

    # Double quotes: "value" or "value # not comment" # real comment
    if stripped.startswith('"'):
        end_idx = stripped.find('"', 1)
        if end_idx != -1:
            val = stripped[1:end_idx]
            remainder = stripped[end_idx + 1 :].strip()
            comment = None
            if remainder.startswith("#"):
                comment = remainder[1:].strip()
            return val, comment

    # Single quotes: 'value'
    if stripped.startswith("'"):
        end_idx = stripped.find("'", 1)
        if end_idx != -1:
            val = stripped[1:end_idx]
            remainder = stripped[end_idx + 1 :].strip()
            comment = None
            if remainder.startswith("#"):
                comment = remainder[1:].strip()
            return val, comment

    # Unquoted value: splits at first unquoted '#'
    if "#" in stripped:
        parts = stripped.split("#", 1)
        val = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else None
        return val, comment

    return stripped, None


def parse_env_text(content: str) -> dict[str, EnvEntry]:
    """Parse text representation of a .env file into a dictionary of entries."""
    entries: dict[str, EnvEntry] = {}
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        match = KEY_ASSIGN_PATTERN.match(trimmed)
        if not match:
            continue

        key = match.group("key")
        is_exported = bool(match.group("export"))
        rest = match.group("rest") or ""

        value, inline_comment = _parse_value_and_comment(rest)
        entries[key] = EnvEntry(
            key=key,
            value=value,
            line_number=idx,
            raw_line=line,
            comment=inline_comment,
            is_exported=is_exported,
        )

    return entries


def parse_env_file(file_path: Path) -> dict[str, EnvEntry]:
    """Parse a .env file from disk. Returns empty dict if file does not exist."""
    if not file_path.is_file():
        return {}
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return parse_env_text(content)
    except OSError:
        return {}
