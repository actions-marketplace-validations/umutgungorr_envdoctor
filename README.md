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
- **Codebase AST / Regex Auditor (`audit`)**: Recursively scans your codebase (`.py`, `.js`, `.ts`) to find environment variables used in code but missing from your `.env.example`.

---

## 🚀 Quick Start

### Installation

```bash
pip install envdoctor-cli
```

### Usage

```bash
# Verify that .env matches .env.example
envdoctor check

# Automatically update .env.example with missing keys (masks values securely)
envdoctor sync

# Scan your Python/JS codebase for variables you forgot to add to .env
envdoctor audit ./src
```

---


## Project case study

EnvDoctor is an open-source project by [Umut Güngör](https://umutgungorr.com/). Read the [EnvDoctor case study](https://umutgungorr.com/projects/envdoctor) for its approach, capabilities, and current scope.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
