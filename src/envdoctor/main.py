"""Main CLI router and commands for EnvDoctor."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .auditor import audit_codebase
from .differ import compare_environments, format_diff_json, format_diff_report
from .parser import parse_env_file
from .syncer import sync_example_file

VERSION = "0.2.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdoctor",
        description="EnvDoctor: Zero-dependency .env & .env.example linter, synchronizer, and code auditor.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Report format: text (human readable) or json (machine parseable)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write report output to specified file path instead of stdout",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color codes in console output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress banner and info messages",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose diagnostic output",
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


def _output(content: str, output_path: Path | None = None) -> None:
    """Helper to emit content to file or stdout."""
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


def handle_check(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    example_path = Path(args.example_file)
    use_no_color = getattr(args, "no_color", False) or ("NO_COLOR" in os.environ)

    if not example_path.exists():
        print(f"Error: Reference template file '{example_path}' was not found.", file=sys.stderr)
        return 2

    if not env_path.exists():
        print(f"Error: Active environment file '{env_path}' does not exist.", file=sys.stderr)
        return 2

    env_map = parse_env_file(env_path)
    example_map = parse_env_file(example_path)

    diff = compare_environments(env_map, example_map, allow_empty=getattr(args, "allow_empty", False))
    strict = getattr(args, "strict", False)

    if args.format == "json":
        json_output = format_diff_json(
            diff,
            env_filename=str(env_path),
            example_filename=str(example_path),
            strict=strict,
        )
        _output(json_output, getattr(args, "output", None))
    else:
        report = format_diff_report(
            diff,
            env_filename=str(env_path),
            example_filename=str(example_path),
            strict=strict,
            no_color=use_no_color,
        )
        _output(report, getattr(args, "output", None))

    if strict:
        return 0 if diff.is_strict_clean() else 1
    return 0 if diff.is_clean else 1


def handle_sync(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    example_path = Path(args.example_file)

    if not env_path.exists():
        print(f"Error: Source environment file '{env_path}' not found.", file=sys.stderr)
        return 2

    env_map = parse_env_file(env_path)
    dry_run = getattr(args, "dry_run", False)
    res = sync_example_file(env_map, example_path, dry_run=dry_run)

    if args.format == "json":
        data = {
            "source_env": str(env_path),
            "target_example": str(example_path),
            "dry_run": dry_run,
            "added_count": len(res.added_keys),
            "added_keys": res.added_keys,
        }
        _output(json.dumps(data, indent=2), getattr(args, "output", None))
        return 0

    if not res.added_keys:
        if not getattr(args, "quiet", False):
            print(f"[V] Already in sync: '{example_path}' has all variables from '{env_path}'.")
        return 0

    mode = "[DRY-RUN] Would append" if dry_run else "[V] Successfully appended"
    lines = [f"{mode} {len(res.added_keys)} variable(s) to '{example_path}':"]
    for line in res.output_lines:
        lines.append(f"    + {line}")
    if dry_run:
        lines.append("\nRun without --dry-run to apply changes.")

    _output("\n".join(lines), getattr(args, "output", None))
    return 0


def handle_audit(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    env_map = parse_env_file(env_path) if env_path.exists() else {}
    known_keys = set(env_map.keys())

    targets = [Path(p) for p in args.paths]
    for t in targets:
        if not t.exists():
            print(f"Error: Target path does not exist: {t}", file=sys.stderr)
            return 2

    res = audit_codebase(targets, known_keys)

    if args.format == "json":
        data = {
            "scanned_paths": [str(p) for p in targets],
            "total_usages": len(res.references),
            "referenced_keys_count": len(res.unique_referenced_keys),
            "known_keys_count": len(known_keys),
            "missing_from_env": sorted(res.missing_from_env),
            "stale_in_env": sorted(res.stale_in_env),
            "references": [
                {
                    "key": r.key,
                    "file_path": r.file_path.replace("\\", "/"),
                    "line_number": r.line_number,
                    "snippet": r.line_snippet,
                }
                for r in res.references
            ],
        }
        _output(json.dumps(data, indent=2), getattr(args, "output", None))
        return 1 if res.missing_from_env else 0

    lines: list[str] = [
        "=" * 68,
        "🩺 EnvDoctor Codebase Audit Report",
        "=" * 68,
        f"  Scanned Paths:       {', '.join(str(p) for p in targets)}",
        f"  Referenced Envs:     {len(res.unique_referenced_keys)} variables across {len(res.references)} usages",
        f"  Known in {env_path.name}:     {len(known_keys)} variables",
        "-" * 68,
    ]

    has_issues = False
    if res.missing_from_env:
        has_issues = True
        lines.append(f"\n[!] MISSING IN {env_path.name} (Code references these, but they are not defined):")
        for k in sorted(res.missing_from_env):
            refs = [r for r in res.references if r.key == k]
            sample = refs[0]
            lines.append(f"    - {k:<24} ({sample.file_path}:{sample.line_number})")

    if res.stale_in_env:
        lines.append(f"\n[*] STALE VARIABLES (Defined in {env_path.name}, but never referenced in scanned code):")
        for k in sorted(res.stale_in_env):
            lines.append(f"    ? {k}")

    lines.append("\n" + "-" * 68)
    if not has_issues:
        lines.append("[V] Clean: All environment variables used in code are defined!")
        _output("\n".join(lines), getattr(args, "output", None))
        return 0

    lines.append("[!] Warning: Found unconfigured environment variables used in code.")
    _output("\n".join(lines), getattr(args, "output", None))
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
        return 0 if exc.code == 0 else 2

    # Default to check command if no subcommand provided
    if not args.command or args.command == "check":
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


if __name__ == "__main__":
    sys.exit(main())
