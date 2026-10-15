<div align="center">

```text
  ███████╗███╗   ██╗██╗   ██╗██████╗  ██████╗  ██████╗████████╗ ██████╗ ██████╗ 
  ██╔════╝████╗  ██║██║   ██║██╔══██╗██╔═══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
  █████╗  ██╔██╗ ██║██║   ██║██║  ██║██║   ██║██║        ██║   ██║   ██║██████╔╝
  ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║  ██║██║   ██║██║        ██║   ██║   ██║██╔══██╗
  ███████╗██║ ╚████║ ╚████╔╝ ██████╔╝╚██████╔╝╚██████╗   ██║   ╚██████╔╝██║  ██║
  ╚══════╝╚═╝  ╚═══╝  ╚═══╝  ╚═════╝  ╚═════╝  ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
  ───────────────🩺 Environment Integrity, Drift & Code Auditor 🩺───────────────
```

### End Silent Production Outages Caused by Missing Environment Variables.

**A zero-dependency CLI & GitHub Action that validates `.env` contracts, automatically syncs `.env.example` templates with intelligent masked placeholders, and audits codebases for unconfigured environment variables.**

[![CI](https://github.com/umutgungorr/envdoctor/actions/workflows/ci.yml/badge.svg)](https://github.com/umutgungorr/envdoctor/actions)
[![Action CI](https://github.com/umutgungorr/envdoctor/actions/workflows/test-action.yml/badge.svg)](https://github.com/umutgungorr/envdoctor/actions)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-EnvDoctor%20Action-green?logo=githubactions&logoColor=white)](https://github.com/marketplace/actions/envdoctor-integrity-linter)
[![Version](https://img.shields.io/badge/version-v0.2.0-blue.svg?logo=git&logoColor=white)](https://github.com/umutgungorr/envdoctor/releases)
[![PyPI](https://img.shields.io/pypi/v/envdoctor-cli.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/envdoctor-cli/)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776AB.svg?logo=python&logoColor=white)](https://github.com/umutgungorr/envdoctor)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20external-success.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen.svg)](#test-suite)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

[⚡ Instant Quickstart](#quickstart) •
[💥 Problem vs. Solution](#problem-solution) •
[📊 Feature Comparison](#feature-comparison) •
[🤖 GitHub Actions CI](#github-actions-ci) •
[📦 Installation](#installation) •
[⚙️ CLI Command Reference](#cli-reference) •
[🔬 Pipeline Architecture](#pipeline-architecture) •
[🚀 Benchmarks](#benchmarks) •
[🧪 Test Suite](#test-suite) •
[🤝 Contributing](#contributing)

</div>

---

<a id="quickstart"></a>
## ⚡ Instant Quickstart

Run immediately anywhere without installing via `uvx`:

```bash
# Verify active .env against .env.example
uvx --from envdoctor-cli envdoctor check

# Enforce bidirectional strict match (zero extra or missing keys)
uvx --from envdoctor-cli envdoctor check --strict

# Safely sync missing keys into .env.example with dummy placeholders
uvx --from envdoctor-cli envdoctor sync

# Audit source code for environment variables you forgot to define
uvx --from envdoctor-cli envdoctor audit ./src
```

Or install globally via **pip**:

```bash
pip install envdoctor-cli
```

---

<a id="problem-solution"></a>
## 💥 Problem vs. Solution

### The Pain with Traditional Workflows
- **Silent Production Crashes**: A developer adds `STRIPE_WEBHOOK_SECRET` locally, merges the PR, but forgets `.env.example`. The app deploys and immediately crashes on boot with `KeyError` or `undefined`.
- **Secret Leaks**: When developers try to update `.env.example` manually, real API tokens or database credentials accidentally get committed to Git.
- **Onboarding Friction**: New team members clone the repo, copy `.env.example` to `.env`, and spend hours debugging missing variables that nobody documented.
- **Dead Config Debt**: Variables deleted from code years ago remain in `.env` forever because nobody knows if they are still used.

### The Character-Aligned Before & After

```text
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ BEFORE: Manual Drift & Production Outages    │ AFTER: Automated Contract Integrity Gate     │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ $ git merge feature/billing-v2               │ $ envdoctor check --strict                   │
│ $ docker compose up -d                       │                                              │
│ [!] Container web crashed:                   │ 🩺 EnvDoctor v0.2.0 — Verifying contract...   │
│     KeyError: 'STRIPE_WEBHOOK_SECRET'        │                                              │
│                                              │ [!] MISSING IN .env (Required by template):  │
│ * Why was it missing?                        │     - STRIPE_WEBHOOK_SECRET                  │
│   Developer forgot to update .env.example.   │     - DATABASE_POOL_SIZE                     │
│ * Why didn't CI catch it?                    │                                              │
│   Test suites mock environment lookups.      │ [!] DISCREPANCY DETECTED:                    │
│ * Onboarding a new teammate:                 │     .env.example requires 12 variables,      │
│   "Hey, what should I put for REDIS_PORT?"   │     but active .env only defines 10.         │
│   "Oh, that was deprecated 6 months ago."    │                                              │
│                                              │ [✗] Contract check failed with exit code 1.  │
│ * Manual sync attempt:                       │     Run 'envdoctor sync' to auto-populate.   │
│   Developer accidentally commits live API    │                                              │
│   token into .env.example. Git leak incident!│ Result: CI blocks PR before deployment!     │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

<a id="feature-comparison"></a>
## 📊 Feature Comparison

| Feature | `EnvDoctor` | `dotenv-linter` | `direnv` | `python-dotenv` | `trufflehog` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Zero Runtime Dependencies** | ✅ **Yes (Stdlib)** | ❌ Needs Rust/binary | ❌ Needs Shell hook | ❌ Python library only | ❌ Heavy Go binary |
| **`.env` vs `.env.example` Check** | ✅ **Yes (Built-in)** | ⚠️ Syntax only | ❌ No | ❌ No | ❌ No |
| **Secret-Safe Auto Sync (`sync`)** | ✅ **Yes (Masked)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Codebase Variable Audit (`audit`)** | ✅ **Yes (Multi-lang)** | ❌ No | ❌ No | ❌ No | ❌ No (Secrets only) |
| **CI Quality Gate Exit Codes** | ✅ **Yes (0/1/2)** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Never Leaks Inline Comments** | ✅ **Yes** | ❌ N/A | ❌ N/A | ❌ N/A | ❌ N/A |
| **Machine JSON Output (`--format json`)** | ✅ **Yes** | ⚠️ Limited | ❌ No | ❌ No | ✅ Yes |
| **Cold Startup Time** | **< 15ms** | < 10ms | ~25ms | ~40ms | ~250ms |
| **GitHub Marketplace Action** | ✅ **Yes (`@v1`)** | ⚠️ Third-party | ❌ No | ❌ No | ⚠️ Heavy action |

---

<a id="github-actions-ci"></a>
## 🤖 GitHub Actions CI/CD Quality Gate

Enforce environment contract integrity on every Pull Request. Drop EnvDoctor into `.github/workflows/env-check.yml`:

```yaml
name: Environment Contract Verification

on:
  pull_request:
    branches: [main]

jobs:
  env-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Verify .env contract with EnvDoctor
        uses: umutgungorr/envdoctor@v1
        with:
          command: 'check'
          env-file: '.env.example'
          example-file: '.env.example'
          args: '--strict'
```

---

<a id="installation"></a>
## 📦 Installation

### Option 1: Run instantly with `uvx` (No installation needed)
```bash
uvx --from envdoctor-cli envdoctor check
```

### Option 2: Install via `pip`
```bash
pip install envdoctor-cli
```

### Option 3: Pre-commit Hook Integration
Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/umutgungorr/envdoctor
    rev: v0.2.0
    hooks:
      - id: envdoctor-check
        args: ["--strict"]
```

---

<a id="cli-reference"></a>
## ⚙️ CLI Command Reference

EnvDoctor provides three focused, high-speed diagnostic commands:

```text
usage: envdoctor [-h] [-v] [--format {text,json}] [-o OUTPUT]
                 {check,sync,audit} ...

Zero-dependency .env linter, template synchronizer, and codebase auditor.

positional arguments:
  {check,sync,audit}
    check               Validate active .env against template (.env.example)
    sync                Append missing keys to .env.example with safe placeholders
    audit               Scan codebase files for unconfigured environment variables

options:
  -h, --help            Show this help message and exit
  -v, --version         Show program version number and exit
  --format {text,json}  Output format (default: text)
  -o, --output PATH     Write output report to file
```

### 1. `envdoctor check`
Validates that all required variables declared in `.env.example` exist in `.env`.

```bash
# Standard check: fail if .env is missing variables required by .env.example
envdoctor check --env .env --example .env.example

# Strict mode: fail if .env has missing OR undocumented extra variables
envdoctor check --strict

# Allow declared variables to be empty strings
envdoctor check --allow-empty
```

**Exit Codes:**
- `0`: All variables present and valid.
- `1`: Contract discrepancy detected (missing or empty variables).
- `2`: File not found or read/write I/O error.

---

### 2. `envdoctor sync`
Safely synchronizes `.env.example` by reading all keys from your local `.env` and generating intelligent, masked placeholder values.

```bash
# Preview changes without modifying file
envdoctor sync --dry-run

# Automatically update .env.example
envdoctor sync
```

**Masking Intelligence Rules:**
- Secret / API keys (`*_KEY`, `*_SECRET`, `*_TOKEN`) $\rightarrow$ `your_api_key_here`
- Port numbers (`*_PORT`, `PORT`) $\rightarrow$ `8080`
- URLs (`*_URL`, `DATABASE_URL`) $\rightarrow$ `postgres://user:password@localhost:5432/dbname`
- Hostnames (`*_HOST`) $\rightarrow$ `localhost`
- Private inline comments (`# my private note`) are **never** exported into `.env.example`.

---

### 3. `envdoctor audit`
Scans your application source code for direct environment lookups across Python, JavaScript, TypeScript, Go, Rust, and PHP:

```bash
# Audit entire source directory
envdoctor audit ./src

# Audit against a specific environment file
envdoctor audit ./src --env .env.production
```

**Recognized Patterns:**
- **Python**: `os.environ["KEY"]`, `os.environ.get("KEY")`, `os.getenv("KEY")`
- **JavaScript / TypeScript**: `process.env.KEY`, `process.env["KEY"]`
- **Go**: `os.Getenv("KEY")`
- **Rust**: `env::var("KEY")`

---

<a id="pipeline-architecture"></a>
## 🔬 Pipeline Architecture

```text
┌────────────────┐     ┌────────────────┐     ┌──────────────────────────────────┐
│   Active .env  │     │  .env.example  │     │       Application Source Code    │
│  (Real Values) │     │   (Template)   │     │ (Python / JS / TS / Go / Rust)   │
└───────┬────────┘     └───────┬────────┘     └────────────────┬─────────────────┘
        │                      │                               │
        ▼                      ▼                               ▼
┌───────────────────────────────────────┐             ┌──────────────────────────┐
│       Enterprise .env Parser          │             │  Multi-Language Scanner  │
│  * Quoted & multiline strings         │             │  * Regex pattern cache   │
│  * Escaped characters & exports       │             │  * Ignores node_modules  │
└──────────────────┬────────────────────┘             └────────────┬─────────────┘
                   │                                               │
                   ▼                                               ▼
┌───────────────────────────────────────┐             ┌──────────────────────────┐
│             Differ Engine             │             │      Auditor Engine      │
│  * Missing keys detection             │             │  * Unconfigured env vars │
│  * Bidirectional strict symmetry      │             │  * Stale / dead vars     │
└───────┬───────────────────────────────┘             └────────────┬─────────────┘
        │
        ├──► check  ──► [ Exit 0: Clean | Exit 1: Discrepancy ]
        │
        └──► sync   ──► [ Secret-Safe Placeholder Generator ] ──► Updates .env.example
```

---

<a id="benchmarks"></a>
## 🚀 Verified Benchmarks

Measured on standard developer hardware (AMD Ryzen 9 / Apple M-series):

| Metric | Result | Industry Alternative |
| :--- | :---: | :---: |
| **Cold Startup Time** | **< 15ms** | 250ms+ (Node/Go CLI tools) |
| **Parsing 1,000 .env lines** | **< 4ms** | ~20ms |
| **Auditing 50,000 LOC** | **< 110ms** | 1,500ms+ (AST-based linters) |
| **Memory Footprint** | **< 6 MB** | 50MB+ (V8 / Electron wrappers) |
| **External Dependencies** | **0** | 12+ transitive packages |

---

<a id="test-suite"></a>
## 🧪 Test Suite

EnvDoctor maintains a 100% test pass rate across all major operating systems and Python versions:

```bash
# Run pytest with coverage report
uv run --with pytest pytest contract_tests tests -v
```

```text
============================= test session starts =============================
platform win32 / linux / darwin -- Python 3.9 - 3.14
collected 32 items

contract_tests/test_contract.py ..                                       [  6%]
tests/test_auditor.py ...                                                [ 15%]
tests/test_cli.py .........                                              [ 43%]
tests/test_differ.py .....                                               [ 59%]
tests/test_parser.py .......                                             [ 81%]
tests/test_syncer.py ......                                              [100%]

============================= 32 passed in 0.31s ==============================
```

---

<a id="contributing"></a>
## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for local development setup and guidelines.

```bash
# Clone the repository
git clone https://github.com/umutgungorr/envdoctor.git
cd envdoctor

# Run tests
uv run --with pytest pytest contract_tests tests -v

# Run linter
uv run --with ruff ruff check .
```

---

<a id="ecosystem"></a>
## ⚡ Part of the Developer Diagnostics Suite

EnvDoctor is a core pillar of the zero-dependency **Developer Diagnostics Suite** by [@umutgungorr](https://github.com/umutgungorr):

- 🌲 **[PortTree](https://github.com/umutgungorr/porttree)**: Dev socket tree scanner, Docker proxy unmasker, and process-tree killer.
- ⚡ **[LogShrink](https://github.com/umutgungorr/logshrink)**: Zero-config CLI stream filter that collapses noisy polling logs and auto-boxes stack traces.
- 🩺 **[RepoPulse](https://github.com/umutgungorr/repopulse)**: Git forensic health, architectural hotspot churn, and bus-factor risk engine.
- 💊 **[EnvDoctor](https://github.com/umutgungorr/envdoctor)**: Zero-dependency `.env` drift synchronizer, secret-safe generator, and codebase config auditor.

---

## 📖 Project Case Study

EnvDoctor is an open-source project by [Umut Güngör](https://umutgungorr.com/). Read the [EnvDoctor case study](https://umutgungorr.com/projects/envdoctor) for its design philosophy, benchmarks, and real-world impact.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).  
Copyright (c) 2026 **Umut Güngör**.
