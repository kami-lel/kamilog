---
name: kamilog
description: Agent guidelines for the kamilog Python logging utility library
---

# kamilog AGENTS

## Project Overview

kamilog is a lightweight Python logging utility that extends Python's built-in `logging` module with structured output, custom log levels, ANSI 16-color support, and flexible timestamp options.

Key additions over stdlib `logging`:

- Custom log levels: `ENTER` (11), `SKIP` (12), `PASS` (21), `SUCC` (22), `DONE` (25), `FAIL` (45)
- `KamiLogger` subclass with `.enter()`, `.skip()`, `.pass_()`, `.succ()`, `.done()`, `.fail()` methods
- `_LogFormatter` producing `LEVEL source: message` (no timestamp by default) with per-level ANSI color
- stdout/stderr split handlers (< WARNING → stdout, >= WARNING → stderr)
- Optional timestamps via `datefmt` parameter (constants: `DATEFMT_TIME`, `DATEFMT_TIME_MS`, `DATEFMT_DATETIME`, `DATEFMT_DATETIME_MS`)
- Relative time display via `relative_to` parameter (elapsed time since a Unix timestamp)
- TTY-aware color (auto-disabled when piped/redirected)
- Level constants (`kamilog.DEBUG`, `kamilog.ENTER`, etc.) re-exported in `__all__`
- Verbosity helpers: `add_verbose_arguments`, `calc_verbosity`, `set_logging_level_by_verbosity`

Repository layout:

```
kamilog/
├── kamilog/
│   ├── __init__.py          # re-exports all public symbols
│   └── kamilog.py           # entire implementation
├── tests/
│   ├── verbosity_test.py    # pytest suite for verbosity helpers
│   └── source_quality_test.py  # banned-marker scan (no TODO/FIXME/HACK/BUG)
├── examples/
│   ├── all_levels.py        # all log levels with descriptions
│   ├── basic_logging.py     # standard + custom levels, three sections
│   ├── logger_names_and_timestamps.py # logger names, timestamps, multiple messages
│   ├── timestamp_formats.py # all four DATEFMT constants
│   ├── relative_time.py     # elapsed time with relative_to
│   └── verbosity.py         # CLI -v/-q/-qq/-qqq flags demo
├── docs/
│   ├── usage_doc.md
│   └── install_guide.md
├── setup.cfg                # package metadata: name, version, author, dependencies
├── setup.py                 # minimal setuptools stub
├── requirements.txt         # pytest (test-only)
├── CHANGELOG.md
└── README.md
```

## Dev Environment

No virtual-environment tooling is pinned; use whichever you prefer (`venv`, `uv`, `pipenv`).

```bash
pip install -e .                  # installs kamilog in editable mode
pip install -r requirements.txt   # installs pytest
```

## Build and Test Commands

There is no build step — the library is distributed by copying source files.

Run the full test suite:

```bash
pytest tests/
```

Run a single test file:

```bash
pytest tests/verbosity_test.py
pytest tests/source_quality_test.py
```

Run a single test:

```bash
pytest tests/verbosity_test.py::TestCalcVerbosity::test2
```

The verbosity test file doubles as a manual smoke-test:

```bash
python tests/verbosity_test.py -vv    # verbosity 2, level DEBUG
python tests/verbosity_test.py -q     # verbosity -1, level WARNING
python tests/verbosity_test.py -qqq   # verbosity -3, level CRITICAL
```

## Code Style

- **Language**: Python 3 — no type annotations; Sphinx/reStructuredText docstrings (`:param:`, `:type:`, `:return:`, `:rtype:`) on all public functions and classes; single-line docstrings on private helpers.
- **String formatting**: use `"".format()` style — not f-strings or `%` formatting.
- **Formatting**: 4-space indentation, PEP 8 naming (`snake_case` functions, `_PrefixedPrivates`, `UPPER_CASE` constants).
- **`__all__`**: both `kamilog.py` and `__init__.py` maintain explicit `__all__` tuples — update both when adding public symbols.
- **No external runtime dependencies** — only the standard library (`logging`, `sys`, `argparse`). Keep it that way.

## Testing Instructions

Tests live in `tests/` and use `pytest` class-based style (`class TestFoo`).

Before committing:

1. `pytest tests/` — all tests must pass with zero failures.
2. `source_quality_test.py` scans both source files for `todo`, `bug`, `fixme`, `hack` (case-insensitive) — do not leave any in `kamilog/kamilog.py` or `kamilog/__init__.py`.

When adding new public functions, add corresponding tests to `tests/verbosity_test.py` or a new `tests/<feature>_test.py` file.

## PR Instructions

- **Branch**: feature branches off `dev`; merge into `dev`. `main` tracks releases.
- **Commit messages**: imperative mood, lowercase, no period — e.g. `add file handler option for getLogger`.
- **CHANGELOG**: update `CHANGELOG.md` under `## [Unreleased]` for every user-visible change before merging.
- **Version bump**: update `__version__` in `kamilog/kamilog.py` and move `[Unreleased]` to a dated version block in `CHANGELOG.md` when cutting a release.
- **Pre-merge checklist**:
  - [ ] `pytest tests/` passes
  - [ ] `__all__` in both `kamilog.py` and `__init__.py` is up to date
  - [ ] CHANGELOG updated
  - [ ] `docs/usage_doc.md` reflects any API changes

## Security Considerations

- Pure logging utility — no network access, file I/O, authentication, or credentials.
- Do not introduce external runtime dependencies without explicit approval.
- Do not commit `.env` files, credentials, or secrets.
