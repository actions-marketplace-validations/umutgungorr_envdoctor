"""Main CLI router and commands for EnvDoctor."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .auditor import audit_codebase
from .differ import compare_environments, format_diff_report
from .parser import parse_env_file
from .syncer import sync_example_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdoctor",
        description="EnvDoctor: Zero-dependency .env & .env.example linter, synchronizer, and code auditor.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: check (default when no command specified)
    check_p = subparsers.add_parser(
        "check",
        help="Compare .env against .env.example and report discrepancies",
    )
    check_p.add_argument(
        "--env",
        dest="env_file",
        default=".env",
        help="Path to active .env file (default: .env)",
    )
    check_p.add_argument(
        "--example",
        dest="example_file",
        default=".env.example",
        help="Path to reference .env.example file (default: .env.example)",
    )
    check_p.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail if variables are missing in .env.example or have empty values",
    )
    check_p.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow empty variable assignments without warnings",
    )

    # Command: sync
    sync_p = subparsers.add_parser(
        "sync",
        help="Safely append missing variables from .env to .env.example with dummy placeholders",
    )
    sync_p.add_argument(
        "--env",
        dest="env_file",
        default=".env",
        help="Path to source .env file (default: .env)",
    )
    sync_p.add_argument(
        "--example",
        dest="example_file",
        default=".env.example",
        help="Path to target .env.example file (default: .env.example)",
    )
    sync_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying the file",
    )

    # Command: audit
    audit_p = subparsers.add_parser(
        "audit",
        help="Scan codebase source files for environment variable lookups",
    )
    audit_p.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Directories or files to scan (default: current directory)",
    )
    audit_p.add_argument(
        "--env",
        dest="env_file",
        default=".env",
        help="Path to active .env file (default: .env)",
    )

    return parser


def handle_check(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    example_path = Path(args.example_file)

    if not example_path.exists():
        print(f"[!] ERROR: Reference template file '{example_path}' was not found.")
        return 1

    if not env_path.exists():
        print(f"[!] CRITICAL: Active environment file '{env_path}' does not exist!")
        return 1

    env_map = parse_env_file(env_path)
    example_map = parse_env_file(example_path)

    diff = compare_environments(env_map, example_map, allow_empty=args.allow_empty)
    report = format_diff_report(
        diff,
        env_filename=str(env_path),
        example_filename=str(example_path),
        strict=args.strict,
    )
    print(report)

    if args.strict:
        return 0 if diff.is_strict_clean() else 1
    return 0 if diff.is_clean else 1


def handle_sync(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    example_path = Path(args.example_file)

    if not env_path.exists():
        print(f"[!] ERROR: Source environment file '{env_path}' not found.")
        return 1

    env_map = parse_env_file(env_path)
    res = sync_example_file(env_map, example_path, dry_run=args.dry_run)

    if not res.added_keys:
        print(f"[V] Already in sync: '{example_path}' has all variables from '{env_path}'.")
        return 0

    mode = "[DRY-RUN] Would append" if args.dry_run else "[V] Successfully appended"
    print(f"{mode} {len(res.added_keys)} variable(s) to '{example_path}':")
    for line in res.output_lines:
        print(f"    + {line}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")
    return 0


def handle_audit(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    env_map = parse_env_file(env_path) if env_path.exists() else {}
    known_keys = set(env_map.keys())

    targets = [Path(p) for p in args.paths]
    res = audit_codebase(targets, known_keys)

    print("=" * 68)
    print("🩺 EnvDoctor Codebase Audit Report")
    print("=" * 68)
    print(f"  Scanned Paths:       {', '.join(str(p) for p in targets)}")
    print(f"  Referenced Envs:     {len(res.unique_referenced_keys)} variables across {len(res.references)} usages")
    print(f"  Known in {env_path.name}:     {len(known_keys)} variables")
    print("-" * 68)

    has_issues = False

    if res.missing_from_env:
        has_issues = True
        print(f"\n[!] MISSING IN {env_path.name} (Code references these, but they are not defined):")
        for k in sorted(res.missing_from_env):
            refs = [r for r in res.references if r.key == k]
            sample = refs[0]
            print(f"    - {k:<24} ({sample.file_path}:{sample.line_number})")

    if res.stale_in_env:
        print(f"\n[*] STALE VARIABLES (Defined in {env_path.name}, but never referenced in scanned code):")
        for k in sorted(res.stale_in_env):
            print(f"    ? {k}")

    print("\n" + "-" * 68)
    if not has_issues:
        print("[V] Clean: All environment variables used in code are defined!")
        return 0

    print("[!] Warning: Found unconfigured environment variables used in code.")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code if exc.code is not None else 0)

    # Default to check command if no subcommand provided
    if not args.command or args.command == "check":
        # Ensure default attributes exist if invoked without subcommand
        if not hasattr(args, "env_file"):
            args.env_file = ".env"
        if not hasattr(args, "example_file"):
            args.example_file = ".env.example"
        if not hasattr(args, "strict"):
            args.strict = False
        if not hasattr(args, "allow_empty"):
            args.allow_empty = False
        return handle_check(args)

    if args.command == "sync":
        return handle_sync(args)

    if args.command == "audit":
        return handle_audit(args)

    return 0
