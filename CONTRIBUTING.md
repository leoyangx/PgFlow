# Contributing to PgFlow

Thank you for your interest in contributing.

PgFlow is built with a simple belief: good tools should feel calm, clear, and humane.
We care deeply about useful features, but we also believe in achieving more with less.

## Branching Strategy

| Branch | Purpose | Stability |
|--------|---------|-----------|
| `main` | Stable releases | Production-ready |
| `nightly` | Experimental features | May have bugs |

**Target `nightly`** for new features, refactoring, API changes.
**Target `main`** for bug fixes, documentation, minor tweaks.

When in doubt, target `nightly`.

## Development Setup

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check pgflow/

# Format
ruff format pgflow/
```

## Code Style

- Line length: 100 characters (`ruff`)
- Target: Python 3.11+
- Linting: `ruff` with rules E, F, I, N, W
- Async: `asyncio` throughout; pytest with `asyncio_mode = "auto"`
- Prefer readable over clever; prefer focused patches over broad rewrites

## Questions?

Open an [issue](https://github.com/leoyangx/PgFlow/issues) or start a discussion.
Thank you for spending your time and care on PgFlow.
