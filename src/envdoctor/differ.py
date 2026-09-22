"""Comparison and diff engine for .env vs .env.example files."""

from __future__ import annotations

import json
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
    no_color: bool = False,
) -> str:
    """Generate a clean, structured CLI report detailing environment differences."""
    red = "" if no_color else "\033[91m"
    green = "" if no_color else "\033[92m"
    yellow = "" if no_color else "\033[93m"
    cyan = "" if no_color else "\033[96m"
    bold = "" if no_color else "\033[1m"
    reset = "" if no_color else "\033[0m"

    lines: list[str] = [
        "=" * 68,
        f"{bold}🩺 EnvDoctor Health Check Report{reset}",
        "=" * 68,
        f"  Active Env File:     {cyan}{env_filename}{reset} ({result.total_env_keys} variables)",
        f"  Reference Template:  {cyan}{example_filename}{reset} ({result.total_example_keys} variables)",
        "-" * 68,
    ]

    has_issues = False

    # 1. Missing in local .env (Critical error)
    if result.missing_in_env:
        has_issues = True
        lines.append(f"\n{red}{bold}[!] CRITICAL: Variables declared in {example_filename} but MISSING in {env_filename}:{reset}")
        for key in result.missing_in_env:
            lines.append(f"    {red}- {key}{reset}")

    # 2. Missing in template .env.example (Warning)
    if result.missing_in_example:
        has_issues = True
        prefix = f"{red}[!]" if strict else f"{yellow}[*]"
        level = "STRICT ERROR" if strict else "WARNING"
        lines.append(
            f"\n{prefix} {level}: Variables defined in {env_filename} but NOT documented in {example_filename}:{reset}"
        )
        for key in result.missing_in_example:
            lines.append(f"    + {key}")

    # 3. Empty values in .env (Warning/Error)
    if result.empty_in_env:
        has_issues = True
        lines.append(f"\n{yellow}[*] NOTICE: Variables defined in {env_filename} but have EMPTY values:{reset}")
        for key in result.empty_in_env:
            lines.append(f"    ? {key}=")

    lines.append("\n" + "-" * 68)
    if not has_issues:
        lines.append(f"{green}✓ PERFECT MATCH: Your environment is fully synchronized and healthy!{reset}")
    elif (not strict and result.is_clean) and (result.missing_in_example or result.empty_in_env):
        lines.append(f"{green}✓ PASS: All required variables are present. (Run `envdoctor sync` to update template).{reset}")
    else:
        lines.append(f"{red}✗ FAILED: Environment discrepancies detected. Please resolve above issues.{reset}")

    lines.append("=" * 68)
    return "\n".join(lines)


def format_diff_json(
    result: DiffResult,
    env_filename: str = ".env",
    example_filename: str = ".env.example",
    strict: bool = False,
) -> str:
    """Format diff result as structured JSON."""
    is_valid = result.is_strict_clean() if strict else result.is_clean
    payload = {
        "valid": is_valid,
        "strict": strict,
        "env_file": env_filename,
        "example_file": example_filename,
        "total_env_keys": result.total_env_keys,
        "total_example_keys": result.total_example_keys,
        "missing_in_env": result.missing_in_env,
        "missing_in_example": result.missing_in_example,
        "empty_in_env": result.empty_in_env,
    }
    return json.dumps(payload, indent=2)
