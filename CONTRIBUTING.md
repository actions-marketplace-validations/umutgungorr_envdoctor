# Contributing to EnvDoctor

Thank you for contributing to EnvDoctor! We welcome improvements, bug reports, and pull requests.

## Development Setup

EnvDoctor has **zero external dependencies** and relies exclusively on Python 3.12+ stdlib.

```bash
# Clone the repository
git clone https://github.com/umutgungorr/envdoctor.git
cd envdoctor

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package with dev dependencies
pip install -e .
pip install pytest ruff
```

## Running Tests & Linters

```bash
# Run test suite
pytest tests contract_tests -v

# Run linter
ruff check .
```
