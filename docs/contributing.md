# Contributing to git-semindex

First off, thank you for considering contributing to `git-semindex`! We appreciate your time and effort.

This document serves as the guide for contributing.

## The Jules Protocol (Agentic Workflow)

This repository leverages agentic workflows for PR management:
- **Agentic Review:** All Pull Requests are reviewed and potentially augmented by **Jules**, our Developer Experience Agent.
- **CI Validation:** Manual merges to `main` are strictly prohibited unless a successful CI pipeline pass has been achieved.

## Development Environment Setup

`git-semindex` has a two-tier architecture: a high-performance Rust core and a Python API. You will need both environments set up.

### Prerequisites

- **Python 3.10+**
- **Rust 1.70+** (Stable toolchain)
- **maturin** (for building the Python/Rust bindings)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/{{OWNER}}/{{REPO}}.git
   cd {{REPO}}
   ```

2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip maturin pytest ruff mypy
   ```

4. **Build and install the package in development mode:**
   ```bash
   make setup # Or run: maturin develop
   ```

### 📱 Termux / Mobile Development

If you are developing on Android using Termux, you must install specific build dependencies before compiling the Rust core:

```bash
pkg install build-essential python-dev pkg-config
```

Ensure your Rust toolchain is configured correctly for your device's architecture (usually `aarch64`).

## Branching Strategy

- **Protected Main:** The `main` branch is protected. Do not commit directly to `main`.
- **Feature Branches:** Create a branch for your work prefixed with `feature/` or `bugfix/` (e.g., `feature/improve-extraction`, `bugfix/fix-linker-issue`).

## Commit Style

We strictly enforce **Conventional Commits** to support automated semantic versioning and changelog generation.

Format your commit messages as follows:
- `feat: add new map-reduce capability`
- `fix: resolve pyo3 memory leak`
- `refactor: optimize git2 bindings`
- `docs: update troubleshooting guide`

A CI action (commitlint) will block PRs that do not follow this standard.

## Testing

Ensure all tests pass before submitting a PR:

- **Rust Tests:** `cargo test`
- **Python Tests:** `pytest tests/`
- **Rust Linting:** `cargo clippy -- -D warnings` and `cargo fmt --check`
- **Python Linting:** `ruff check .` and `mypy git_semindex`

You can use the provided `Makefile` to simplify these commands (e.g., `make test`, `make lint`).
