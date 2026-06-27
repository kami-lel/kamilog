---
name: kamilog AGENTS
alwaysApply: true
---

# kamilog AGENTS

kamilog is a lightweight Python logging utility extending the stdlib `logging` module. See [`CONTEXT.md`](CONTEXT.md) for architecture, module layout, and feature details.

## Setup Commands

```bash
pip install -e .                  # installs kamilog in editable mode
pip install -r requirements.txt   # installs pytest (test-only dependency)
```

No virtual-environment tooling is pinned; use whichever you prefer (`venv`, `uv`, `pipenv`).

## Build and Test Commands

There is no build step — the library is distributed by copying source files.

Run the full test suite:

```bash
pytest tests/
```

Run a single test file or test:

```bash
pytest tests/verbosity_test.py
pytest tests/verbosity_test.py::TestCalcLoggingLevel::test_v2
```

The verbosity test doubles as a manual smoke-test:

```bash
python tests/verbosity_test.py -vvv   # verbosity 3, level DEBUG
python tests/verbosity_test.py -q     # verbosity -1, level WARNING
```

Scope tests to the changed module before pushing — `tests/verbosity_test.py` for verbosity helpers, `tests/source_quality_test.py` for banned-marker scan.

## Code Style

- **Language**: Python 3 — no type annotations
- **Docstrings**: Sphinx/reStructuredText style (`:param:`, `:type:`, `:return:`, `:rtype:`) on all public classes and functions; single-line docstrings on private helpers; `__init__` carries no docstring — documented by the class docstring
- **String formatting**: `"".format()` only — not f-strings or `%`
- **Naming**: `snake_case` functions, `_PrefixedPrivate` classes, `UPPER_CASE` constants; 4-space indentation, PEP 8 throughout
- **`__all__`**: both `kamilog/kamilog.py` and `kamilog/__init__.py` maintain explicit `__all__` tuples — update both when adding public symbols
- **Dependencies**: no external runtime dependencies; stdlib only (`logging`, `sys`, `collections`, `argparse`) — do not introduce new ones without explicit approval

## Testing Instructions

Tests live in `tests/` and use `pytest` class-based style (`class TestFoo`).

Before merging:

1. `pytest tests/` — all 16 tests must pass with zero failures.
2. `tests/source_quality_test.py` scans `kamilog/kamilog.py` and `kamilog/__init__.py` for `todo`, `bug`, `fixme`, `hack` (case-insensitive) — leave none behind.

When adding new public functions, add corresponding tests to an appropriate `tests/<feature>_test.py` file.

## PR & Commit Instructions

- **Branch**: feature branches off `dev`; merge into `dev`. `main` tracks releases only.
- **Commit messages**: imperative mood, lowercase, no period — e.g. `add diff-only message filter`.
- **CHANGELOG**: update `CHANGELOG.md` under `## [Unreleased]` for every user-visible change before merging.
- **Version bump**: update `__version__` in `kamilog/kamilog.py` and move `[Unreleased]` to a dated version block when cutting a release.

Pre-merge checklist:

- [ ] `pytest tests/` passes
- [ ] `__all__` in both `kamilog.py` and `__init__.py` is up to date
- [ ] CHANGELOG updated
- [ ] `docs/usage_doc.md` reflects any API changes
- [ ] `CONTEXT.md` updated if architecture or module layout changed

## Documentation Maintenance

Keep these files in sync with code changes:

| file | update when |
| --- | --- |
| `CHANGELOG.md` | any user-visible change |
| `AGENTS.md` | commands, conventions, or constraints change |
| `CONTEXT.md` | architecture, module layout, or feature set changes |
| `docs/usage_doc.md` | public API or output format changes |
| `docs/install_guide.md` | installation steps or requirements change |

## Security Considerations

- Pure logging utility — no network access, file I/O, authentication, or credentials.
- Do not introduce external runtime dependencies without explicit approval.
- Do not commit `.env` files, credentials, or secrets.
