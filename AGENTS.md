---
name: kamilog
description: Agent guidelines for the kamilog Python logging utility library
---

# kamilog AGENTS

## Project Overview

kamilog is a lightweight Python logging utility (`kamilog/kamilog.py`) that wraps Python's built-in `logging` module with a cleaner output format. It provides:

- Padded 5-character log level names (`INFO `, `WARN `, `CRIT `) for consistent alignment
- A `getLogger()` drop-in that configures a console `StreamHandler` exactly once per logger name
- Verbosity helpers (`add_verbose_arguments`, `calc_verbosity`, `set_logging_level_by_verbosity`) that wire `-v`/`-q` CLI flags to logging levels

Repository layout:

```
kamilog/
├── kamilog/
│   ├── __init__.py        # re-exports all public symbols
│   └── kamilog.py         # entire implementation + module docstring
├── tests/
│   └── verbosity_test.py  # pytest suite for verbosity helpers
├── requirements.txt        # pytest (test-only dependency)
├── CHANGELOG.md
└── README.md
```

Current version: `1.2.1-alpha` (defined in `kamilog/kamilog.py` as `__version__`).

## Dev Environment Tips

No virtual-environment tooling is pinned; use whichever you prefer (`venv`, `uv`, `pipenv`).

```bash
pip install -r requirements.txt   # installs pytest
```

The package is not installed via pip; tests use a `sys.path.insert` to resolve the local source, so no `pip install -e .` is required.

## Build and Test Commands

There is no build step — the library is distributed by copying source files.

Run the full test suite:

```bash
pytest tests/
```

Run a single test class:

```bash
pytest tests/verbosity_test.py::TestCalcVerbosity
```

Run a single test:

```bash
pytest tests/verbosity_test.py::TestCalcVerbosity::test2
```

The verbosity test file also doubles as a manual CLI smoke-test:

```bash
python tests/verbosity_test.py -vv    # verbosity 2, level DEBUG
python tests/verbosity_test.py -q     # verbosity -1, level CRITICAL+1
```

## Code Style

- **Language**: Python 3 — no type annotations are used; Sphinx/reStructuredText docstrings (`:param:`, `:type:`, `:return:`, `:rtype:`) on all public functions.
- **Docstrings**: module-level docstring in `kamilog.py` is the canonical documentation source; keep it in sync with `README.md`.
- **Formatting**: no formatter is enforced, but the existing code uses 4-space indentation and PEP 8 naming (`snake_case` functions, `_PrefixedPrivates`).
- **`__all__`**: both `kamilog.py` and `__init__.py` maintain explicit `__all__` tuples — update both when adding public symbols.
- **No external runtime dependencies** — only the standard library (`logging`, `argparse`). Keep it that way.

## Testing Instructions

All tests live in `tests/verbosity_test.py` and use `pytest` class-based style (`class TestFoo`).

Before committing:

1. `pytest tests/` — all tests must pass with zero failures.
2. Verify no `TODO` or `FIXME` comments were accidentally left in `kamilog/kamilog.py` or `kamilog/__init__.py` (the README has a tracked todo about adding a test for this).

When adding new public functions, add corresponding test classes to `tests/verbosity_test.py` or a new `tests/<feature>_test.py` file.

## PR Instructions

- **Branch**: feature branches off `dev`; merge into `dev`. `main` tracks releases.
- **Commit messages**: imperative mood, lowercase, no period — e.g. `add file handler option for getLogger`.
- **CHANGELOG**: update `CHANGELOG.md` under `## [Unreleased]` for every user-visible change before merging.
- **Version bump**: update `__version__` in `kamilog/kamilog.py` and move `[Unreleased]` to a dated version block in `CHANGELOG.md` when cutting a release.
- **Pre-merge checklist**:
  - [ ] `pytest tests/` passes
  - [ ] `__all__` in both files is up to date
  - [ ] CHANGELOG updated
  - [ ] Module docstring in `kamilog.py` reflects any API changes

## Security Considerations

- This is a pure logging utility with no network access, file I/O, authentication, or credentials. Security surface is minimal.
- Do not introduce external runtime dependencies without explicit approval — the zero-dependency contract is intentional.
- Do not commit `.env` files, credentials, or secrets; `.gitignore` already excludes `.env` and `.envrc`.
