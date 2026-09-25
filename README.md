# EnvDoctor 🩺

[![PyPI version](https://img.shields.io/pypi/v/envdoctor-cli.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/envdoctor-cli/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/envdoctor-cli.svg?style=flat-square)](https://pypi.org/project/envdoctor-cli/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)]()

> **Zero-dependency `.env` and `.env.example` linter, synchronizer, and code auditor CLI with JSON output.**  
> Prevent missing environment variables, eliminate production deployment crashes, and keep your config templates perpetually synchronized.

<p align="center">
  <img src="assets/demo.png" alt="EnvDoctor Demo" width="850">
</p>

```text
$ envdoctor check --strict

🩺 EnvDoctor v0.2.0 — Verifying environment contract...
[!] MISSING IN .env (Required by .env.example):
    - STRIPE_SECRET_KEY
    - DATABASE_POOL_SIZE

[!] DISCREPANCY DETECTED:
    .env.example requires 12 variables, but active .env only defines 10.

[✗] Contract check failed with exit code 1.
    (To safely sync missing placeholders, run: envdoctor sync)
```

---

## 💥 The Problem

In modern software projects, environment variables are essential for configuration and secrets. However, teams constantly face these issues:
1. **Silent Production Outages**: A developer adds a new variable (e.g. `STRIPE_KEY` or `DATABASE_URL`) to their local `.env`, forgets to update `.env.example`, and production crashes immediately upon deployment.
2. **Onboarding Friction**: New team members clone the repo, copy `.env.example` to `.env`, but discover missing or undocumented variables only after runtime errors.
3. **Dead / Stale Config Clutter**: Variables deleted from source code remain lingering in `.env` files indefinitely because nobody knows if they are still needed.

**EnvDoctor** solves this entirely with three focused, zero-dependency tools: `check`, `sync`, and `audit`.

---

## 🌟 Key Features

- **Zero External Dependencies**: Built 100% on the Python Standard Library (`re`, `pathlib`, `argparse`, `json`, `os`). Runs immediately anywhere without package installation overhead.
- **Enterprise `.env` Parser**: Handles single/double quotes, multiline values across physical lines (certificates, JSON blobs), escaped quotes (`\"`, `\'`), inline comments (`#`), and `export` statements.
- **Machine-Parseable JSON Output**: `--format json` support across all subcommands (`check`, `sync`, `audit`) for easy integration into automation pipelines.
- **Safe Template Synchronizer (`sync`)**: Automatically populates `.env.example` using keys from `.env`, substituting real secrets with intelligent masked placeholders (e.g. `your_api_key_here`, `8080`, `localhost`).
- **Codebase AST / Regex Auditor (`audit`)**: Recursively scans Python (`os.environ`, `os.getenv`) and JavaScript/TypeScript (`process.env`) files to find environment variables used in code but missing from `.env`.
- **Deterministic Exit Codes**: `0` (clean), `1` (contract violations / missing keys), `2` (CLI / file not found errors).

---

## 🚀 Quick Start

### 1. Installation

Install via pip from PyPI:

```bash
pip install envdoctor-cli
```

Or run directly without installation:

```bash
python -m envdoctor --help
```

---

## 🛠️ Commands & Usage

### 1. `envdoctor check` (Compare & Lint)

Compare your local `.env` against the reference `.env.example`:

```bash
# Standard check (fails if required template variables are missing locally)
envdoctor check

# Custom file paths
envdoctor check --env .env.local --example .env.template

# Strict mode (fails if template is missing any local variables or values are empty)
envdoctor check --strict

# Machine-readable JSON output
envdoctor --format json -o diff_report.json check
```

**Sample Output:**
```text
====================================================================
🩺 EnvDoctor Health Check Report
====================================================================
  Active Env File:     .env (12 variables)
  Reference Template:  .env.example (14 variables)
--------------------------------------------------------------------

[!] CRITICAL: Variables declared in .env.example but MISSING in .env:
    - REDIS_URL
    - STRIPE_WEBHOOK_SECRET

--------------------------------------------------------------------
✗ FAILED: Environment discrepancies detected. Please resolve above issues.
====================================================================
```

---

### 2. `envdoctor sync` (Safe Template Generation)

Safely sync newly added local `.env` variables to `.env.example` without exposing real secrets:

```bash
# Preview what would be appended
envdoctor sync --dry-run

# Append new variables with masked dummy placeholders
envdoctor sync
```

EnvDoctor automatically generates safe values:
- `PORT` $\rightarrow$ `8080`
- `DATABASE_URL` $\rightarrow$ `postgresql://postgres:password@localhost:5432/my_database`
- `STRIPE_KEY` $\rightarrow$ `your_stripe_key_here`
- `DEBUG` $\rightarrow$ `true`

---

### 3. `envdoctor audit` (Scan Source Code)

Scan your application code to find environment variables that aren't defined in `.env`:

```bash
# Scan current directory
envdoctor audit

# Scan specific directories
envdoctor audit src/ backend/ --env .env

# Export audit findings to JSON
envdoctor --format json -o audit.json audit src/
```

**Sample Output:**
```text
====================================================================
🩺 EnvDoctor Codebase Audit Report
====================================================================
  Scanned Paths:       src/, backend/
  Referenced Envs:     18 variables across 42 usages
  Known in .env:       16 variables
--------------------------------------------------------------------

[!] MISSING IN .env (Code references these, but they are not defined):
    - ANALYTICS_ID             (src/services/telemetry.py:14)

[*] STALE VARIABLES (Defined in .env, but never referenced in scanned code):
    - LEGACY_FEATURE_V1
====================================================================
```

---

## ⚙️ CLI Options & Deterministic Exit Codes

```text
usage: envdoctor [-h] [--version] [--format {text,json}] [-o OUTPUT]
                 [--no-color] [-q] [-v] {check,sync,audit} ...
```

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success: Environment is in sync / clean audit / dry-run |
| `1` | Discrepancy detected: Missing variables in `.env`, strict failure, or missing code variables |
| `2` | Error: File not found or invalid CLI arguments |

---

## 🤖 CI/CD Integration (GitHub Actions)

Catch missing environment variables before merging PRs:

```yaml
name: Configuration Integrity

on: [push, pull_request]

jobs:
  envdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Verify Environment Template
        run: |
          python -m envdoctor --format json check --strict --example .env.example --env .env.example
```

---

## 🧪 Running Tests

```bash
uv run --with pytest pytest
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
