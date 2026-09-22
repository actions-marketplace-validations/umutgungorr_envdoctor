"""Comparison and diff engine for .env vs .env.example files."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .parser import EnvEntry


@dataclass(slots=True)
class DiffResult:
    missing_in_env: list[str]
    missing_in_example: list[str]
    empty_in_env: list[str]
    total_env_keys: int
    total_example_keys: int

    @property
    def is_clean(self) -> bool:
        """Returns True if there are zero missing keys in .env."""
        return len(self.missing_in_env) == 0

    def is_strict_clean(self) -> bool:
        """Returns True if both files are perfectly in sync (no missing keys either way)."""
        return self.is_clean and len(self.missing_in_example) == 0 and len(self.empty_in_env) == 0


def compare_environments(
    env_map: Mapping[str, EnvEntry],
    example_map: Mapping[str, EnvEntry],
    allow_empty: bool = False,
) -> DiffResult:
    """Compare local .env entries against template .env.example entries."""
    env_keys = set(env_map.keys())
    example_keys = set(example_map.keys())

    missing_in_env = sorted(example_keys - env_keys)
    missing_in_example = sorted(env_keys - example_keys)

    empty_in_env: list[str] = []
    if not allow_empty:
        for k, entry in env_map.items():
            if not entry.value.strip():
                empty_in_env.append(k)
        empty_in_env.sort()

    return DiffResult(
        missing_in_env=missing_in_env,
        missing_in_example=missing_in_example,
        empty_in_env=empty_in_env,
        total_env_keys=len(env_keys),
        total_example_keys=len(example_keys),
    )


def format_diff_report(
    result: DiffResult,
    env_filename: str = ".env",
    example_filename: str = ".env.example",
    strict: bool = False,
) -> str:
    """Generate a clean, structured CLI report detailing environment differences."""
    lines: list[str] = [
        "=" * 68,
        "🩺 EnvDoctor Health Check Report",
        "=" * 68,
        f"  Active Env File:     {env_filename} ({result.total_env_keys} variables)",
        f"  Reference Template:  {example_filename} ({result.total_example_keys} variables)",
        "-" * 68,
    ]

    has_issues = False

    # 1. Missing in local .env (Critical error)
    if result.missing_in_env:
        has_issues = True
        lines.append(f"\n[!] CRITICAL: Variables declared in {example_filename} but MISSING in {env_filename}:")
        for key in result.missing_in_env:
            lines.append(f"    - {key}")

    # 2. Missing in template .env.example (Warning)
    if result.missing_in_example:
        has_issues = True
        prefix = "[!]" if strict else "[*]"
        level = "STRICT ERROR" if strict else "WARNING"
        lines.append(
            f"\n{prefix} {level}: Variables defined in {env_filename} but NOT documented in {example_filename}:"
        )
        for key in result.missing_in_example:
            lines.append(f"    + {key}")

    # 3. Empty values in .env (Warning/Error)
    if result.empty_in_env:
        has_issues = True
        lines.append(f"\n[*] NOTICE: Variables defined in {env_filename} but have EMPTY values:")
        for key in result.empty_in_env:
            lines.append(f"    ? {key}=")

    lines.append("\n" + "-" * 68)
    if not has_issues:
        lines.append("✓ PERFECT MATCH: Your environment is fully synchronized and healthy!")
    elif (not strict and result.is_clean) and (result.missing_in_example or result.empty_in_env):
        lines.append("✓ PASS: All required variables are present. (Run `envdoctor sync` to update template).")
    else:
        lines.append("✗ FAILED: Environment discrepancies detected. Please resolve above issues.")

    lines.append("=" * 68)
    return "\n".join(lines)
