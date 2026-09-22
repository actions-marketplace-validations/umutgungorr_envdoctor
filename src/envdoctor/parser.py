"""Parser implementation for .env and .env.example files.

Supports:
- Standard KEY=VALUE pairs
- export KEY=VALUE statements
- Quoted values (single or double quotes)
- Multiline values spanning across physical lines
- Escaped quotes and characters (\\", \\', \\n)
- Inline comments (#)
- Empty values and blank lines
"""

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


# Matches key assignment start: optional 'export ', key name, '=', followed by rest of line
KEY_ASSIGN_PATTERN = re.compile(
    r"^(?P<export>export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<rest>.*)$"
)


def _unescape_double_quotes(val: str) -> str:
    """Unescape standard escapes in double-quoted strings."""
    return (
        val.replace(r'\"', '"')
        .replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\t", "\t")
        .replace(r"\\", "\\")
    )


def _unescape_single_quotes(val: str) -> str:
    """Unescape standard single quotes in single-quoted strings."""
    return val.replace(r"\'", "'").replace(r"\\", "\\")


def parse_env_text(content: str) -> dict[str, EnvEntry]:
    """Parse text representation of a .env file into a dictionary of entries."""
    entries: dict[str, EnvEntry] = {}
    lines = content.splitlines()
    num_lines = len(lines)
    idx = 0

    while idx < num_lines:
        line = lines[idx]
        line_num = idx + 1
        trimmed = line.strip()

        # Skip empty lines or pure comment lines
        if not trimmed or trimmed.startswith("#"):
            idx += 1
            continue

        match = KEY_ASSIGN_PATTERN.match(trimmed)
        if not match:
            idx += 1
            continue

        key = match.group("key")
        is_exported = bool(match.group("export"))
        rest = match.group("rest") or ""

        # Case 1: Double-quoted value, potentially spanning multiple lines
        if rest.startswith('"'):
            # Check if closed on same line (accounting for escaped quotes)
            val_chars: list[str] = []
            escaped = False
            closed = False
            comment = None

            # Parse through first line rest[1:]
            char_idx = 1
            while char_idx < len(rest):
                c = rest[char_idx]
                if escaped:
                    val_chars.append(c)
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == '"':
                    closed = True
                    char_idx += 1
                    break
                else:
                    val_chars.append(c)
                char_idx += 1

            if closed:
                # Value was closed on the same line
                remainder = rest[char_idx:].strip()
                if remainder.startswith("#"):
                    comment = remainder[1:].strip()
                value = "".join(val_chars)
            else:
                # Value spans across subsequent lines until unescaped '"'
                val_chars.append("\n")
                idx += 1
                while idx < num_lines:
                    current_line = lines[idx]
                    char_idx = 0
                    while char_idx < len(current_line):
                        c = current_line[char_idx]
                        if escaped:
                            val_chars.append(c)
                            escaped = False
                        elif c == "\\":
                            escaped = True
                        elif c == '"':
                            closed = True
                            char_idx += 1
                            break
                        else:
                            val_chars.append(c)
                        char_idx += 1
                    if closed:
                        remainder = current_line[char_idx:].strip()
                        if remainder.startswith("#"):
                            comment = remainder[1:].strip()
                        break
                    val_chars.append("\n")
                    idx += 1
                value = "".join(val_chars)

            entries[key] = EnvEntry(
                key=key,
                value=_unescape_double_quotes(value),
                line_number=line_num,
                raw_line=line,
                comment=comment,
                is_exported=is_exported,
            )
            idx += 1
            continue

        # Case 2: Single-quoted value, potentially spanning multiple lines
        if rest.startswith("'"):
            val_chars = []
            escaped = False
            closed = False
            comment = None

            char_idx = 1
            while char_idx < len(rest):
                c = rest[char_idx]
                if escaped:
                    val_chars.append(c)
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == "'":
                    closed = True
                    char_idx += 1
                    break
                else:
                    val_chars.append(c)
                char_idx += 1

            if closed:
                remainder = rest[char_idx:].strip()
                if remainder.startswith("#"):
                    comment = remainder[1:].strip()
                value = "".join(val_chars)
            else:
                val_chars.append("\n")
                idx += 1
                while idx < num_lines:
                    current_line = lines[idx]
                    char_idx = 0
                    while char_idx < len(current_line):
                        c = current_line[char_idx]
                        if escaped:
                            val_chars.append(c)
                            escaped = False
                        elif c == "\\":
                            escaped = True
                        elif c == "'":
                            closed = True
                            char_idx += 1
                            break
                        else:
                            val_chars.append(c)
                        char_idx += 1
                    if closed:
                        remainder = current_line[char_idx:].strip()
                        if remainder.startswith("#"):
                            comment = remainder[1:].strip()
                        break
                    val_chars.append("\n")
                    idx += 1
                value = "".join(val_chars)

            entries[key] = EnvEntry(
                key=key,
                value=_unescape_single_quotes(value),
                line_number=line_num,
                raw_line=line,
                comment=comment,
                is_exported=is_exported,
            )
            idx += 1
            continue

        # Case 3: Unquoted value (split on unquoted '#')
        comment = None
        if "#" in rest:
            parts = rest.split("#", 1)
            val = parts[0].strip()
            comment = parts[1].strip() if len(parts) > 1 else None
        else:
            val = rest.strip()

        entries[key] = EnvEntry(
            key=key,
            value=val,
            line_number=line_num,
            raw_line=line,
            comment=comment,
            is_exported=is_exported,
        )
        idx += 1

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
