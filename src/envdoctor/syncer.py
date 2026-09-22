"""Template synchronizer: safely updates .env.example with dummy placeholders."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .parser import EnvEntry


@dataclass(slots=True)
class SyncResult:
    added_keys: list[str]
    skipped_keys: list[str]
    output_lines: list[str]
    was_written: bool


def generate_safe_placeholder(key: str, real_value: str = "") -> str:
    """Generate a safe, masked dummy placeholder based on variable naming conventions."""
    upper = key.upper()
    lower = key.lower()

    if upper.endswith("_PORT") or upper == "PORT":
        return "8080"
    if "DATABASE_URL" in upper or "DB_URL" in upper:
        return "postgresql://postgres:password@localhost:5432/my_database"
    if upper.endswith("_HOST") or upper == "HOST":
        return "localhost"
    if "REDIS_URL" in upper:
        return "redis://localhost:6379/0"
    if upper in {"DEBUG", "VERBOSE"}:
        return "true"
    if upper.endswith("_ENABLED") or upper.startswith("ENABLE_"):
        return "false"
    if "EMAIL" in upper:
        return "user@example.com"
    if "API_URL" in upper:
        return "https://api.example.com/v1"

    # Default for secrets, keys, and tokens
    return f"your_{lower}_here"


def sync_example_file(
    env_map: Mapping[str, EnvEntry],
    example_path: Path,
    dry_run: bool = False,
) -> SyncResult:
    """Safely append missing keys from .env into .env.example with masked placeholders."""
    existing_example_content = ""
    existing_keys: set[str] = set()

    if example_path.is_file():
        try:
            existing_example_content = example_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            existing_example_content = ""

    from .parser import parse_env_text

    parsed_example = parse_env_text(existing_example_content)
    existing_keys = set(parsed_example.keys())

    added_keys: list[str] = []
    skipped_keys: list[str] = []
    new_lines: list[str] = []

    for key, entry in sorted(env_map.items()):
        if key in existing_keys:
            skipped_keys.append(key)
            continue

        placeholder = generate_safe_placeholder(key, entry.value)
        comment_suffix = f" # {entry.comment}" if entry.comment else ""
        export_prefix = "export " if entry.is_exported else ""
        new_lines.append(f"{export_prefix}{key}={placeholder}{comment_suffix}")
        added_keys.append(key)

    if not added_keys:
        return SyncResult(
            added_keys=[],
            skipped_keys=skipped_keys,
            output_lines=[],
            was_written=False,
        )

    # Prepare appended content
    separator = "\n" if existing_example_content.endswith("\n") or not existing_example_content else "\n\n"
    header = "# Synchronized by EnvDoctor\n"
    content_to_append = separator + header + "\n".join(new_lines) + "\n"

    final_content = existing_example_content + content_to_append

    if not dry_run:
        try:
            example_path.write_text(final_content, encoding="utf-8")
            was_written = True
        except OSError:
            was_written = False
    else:
        was_written = False

    return SyncResult(
        added_keys=added_keys,
        skipped_keys=skipped_keys,
        output_lines=new_lines,
        was_written=was_written,
    )
