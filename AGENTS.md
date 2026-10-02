---
name: kamilog AGENTS
alwaysApply: true
---

# kamilog AGENTS

kamilog is a lightweight Python logging utility extending the stdlib `logging` module. See [`CONTEXT.md`](CONTEXT.md) for architecture, module layout, and feature details.

## Setup Commands

```bash
pip install -e . --group dev   # installs kamilog in editable mode plus pytest (test-only dependency)
```

No virtual-environment tooling is pinned; use whichever you prefer (`venv`, `uv`, `pipenv`).

## Build and Test Commands

There is no build step; kamilog is installed as a package (`pip install .`).

Run the full suite (scope to the changed area otherwise):

```bash
pytest tests/
```

Run a single test file or test:

```bash
pytest tests/v/v-calc_logging_level_test.py
pytest tests/v/v-calc_logging_level_test.py::TestCalcLoggingLevel::test_v2
```

## Code Style

- **Language**: Python 3 — no type annotations
- **Docstrings**: Sphinx/reStructuredText style (`:param:`, `:type:`, `:return:`, `:rtype:`) on all public classes and functions; single-line docstrings on private helpers; `__init__` carries no docstring — documented by the class docstring
- **String formatting**: `"".format()` only — not f-strings or `%`
- **Naming**: `snake_case` functions, `_PrefixedPrivate` classes, `UPPER_CASE` constants; 4-space indentation, PEP 8 throughout
- **Dependencies**: stdlib only (no new runtime dependency without explicit approval)
- **`__all__`**: `kamilog/__init__.py` holds the explicit `__all__` tuple and imports every public name from its module — when adding a public symbol, import it there and add it to `__all__`

## Testing Instructions

Tests live in `tests/` and use `pytest` class-based style (`class TestFoo`).

Before merging:

1. `pytest tests/` — all tests must pass.
2. `tests/source_quality_test.py` scans every `kamilog/*.py` module for `todo`, `bug`, `fixme`, `hack` (case-insensitive) — leave none behind.

When adding new public functions, add corresponding tests under the relevant subdirectory — `tests/v/` for verbosity helpers (named `v-<feature>_test.py`), `tests/cb/` for comment-banner functions (named `cb-<feature>_test.py`), `tests/ansi/` for `AnsiRenderer`/TTY detection, `tests/lf/` for `_LogFormatter`/`_LogFormatEngine`, `tests/badge/` for badges (named `badge-<feature>_test.py`), `tests/logger/` for `KamiLogger` behavior, `tests/deed/` for deed methods (named `deed-<feature>_test.py`), `tests/dof/` for diff-only compression, `tests/tal/` for `_TabAlignedLine`, `tests/cli/` for CLI subcommand flags (named `cli-<feature>_test.py`). Every `examples/` demo script has a matching golden-output test under `tests/<area>/demo/` — add or update one when a demo script's output changes.

## PR & Commit Instructions

- **Branch**: feature branches off `dev`; merge into `dev`. `main` tracks releases only.
- **Commit messages**: imperative mood, lowercase, no period — e.g. `add diff-only message filter`.
- **CHANGELOG**: update `CHANGELOG.md` under `## [Unreleased]` for every user-visible change before merging.
- **Version bump**: set `__version__` in `kamilog/__init__.py` and move `[Unreleased]` to a dated version block when cutting a release.

Pre-merge checklist:

- [ ] `pytest tests/` passes
- [ ] `__all__` in `kamilog/__init__.py` is up to date
- [ ] CHANGELOG updated
- [ ] the matching topic guide under `docs/` reflects any API changes
- [ ] `CONTEXT.md` updated if architecture or module layout changed

## Documentation Maintenance

Keep these files in sync with code changes:

| file | update when |
| --- | --- |
| `CHANGELOG.md` | any user-visible change |
| `AGENTS.md` | commands, conventions, or constraints change |
| `CONTEXT.md` | architecture, module layout, or feature set changes |
| `README.md` | installation steps or requirements change, or a file is added to `docs/` (link it there and cross-link it from related guides) |
| [`docs/log-doc.md`](docs/log-doc.md) | log levels, timestamps, diff-only output, or file output change |
| [`docs/ansi-doc.md`](docs/ansi-doc.md) | `AnsiStyle` or `AnsiRenderer` change |
| [`docs/banner-doc.md`](docs/banner-doc.md) | comment banner functions change |
| [`docs/verbosity-doc.md`](docs/verbosity-doc.md) | verbosity helpers, `-v`/`-q` flags, or level mapping change |
| [`docs/shim-doc.md`](docs/shim-doc.md) | `scripts/kamilog_shim.sh` or its fallbacks change |
| [`docs/badge-doc.md`](docs/badge-doc.md) | badge API, native badges, or badge display change |
| [`docs/deed-doc.md`](docs/deed-doc.md) | deed methods, wording, levels, track form, or `deed` CLI change |

## Security Considerations

- Pure logging utility: no network, credentials, or auth; no committed `.env` or secrets
