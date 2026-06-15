# kamilog CHANGELOG

[^format]
















## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

[unreleased]: https://github.com/kami-lel/kamilog/compare/v1.3.1...dev















## [1.3.1] - 2026-06-16

### Changed

- `set_logging_level_by_verbosity()` now accepts a `logger` instance directly via
  the `logger` parameter

[1.3.1]: https://github.com/kami-lel/kamilog/compare/v1.3.0...v1.3.1













## [1.3.0] - 2026-06-16

### Added

Custom log levels:

- `KamiLogger`, a `logging.Logger` subclass adding four levels — `ENTER` (11),
  `SKIP` (12), `PASS` (25), `FAIL` (45) — with matching `.enter()`, `.skip()`,
  `.pass_()`, `.fail()` methods
- all log-level constants exposed on the `kamilog` namespace (`kamilog.DEBUG`,
  `kamilog.ENTER`, etc.) — `import logging` no longer needed for level constants

Output formatting:

- structured log format `HH:MM:SS [LEVEL] source:\tmessage`
- ANSI 16-color output: datetime in black, level name colored per severity,
  message uncolored
- color auto-disabled when stdout/stderr is not a TTY (piped or redirected)
- separate stdout handler (below `WARNING`) and stderr handler (`WARNING` and above)

Timestamps:

- `datefmt` parameter on `getLogger()` to control timestamp format
- `relative_to` parameter on `getLogger()` to display elapsed time instead of
  wall-clock time (supports negative values)
- four timestamp format constants: `DATEFMT_TIME`, `DATEFMT_TIME_MS`,
  `DATEFMT_DATETIME`, `DATEFMT_DATETIME_MS`

Packaging:

- `setup.cfg` and `setup.py` — package is now pip-installable
  (`pip install .` / `pip install -e .`); `setup.cfg` reads `version` and
  `author` from `kamilog/kamilog.py` via the `attr:` directive

Documentation, tests & examples:

- `AGENTS.md` with contributor and agent guidelines
- `docs/install_guide.md` and `docs/usage_doc.md` (extracted from README)
- Sphinx/reStructuredText docstrings on all public classes, functions, and
  `_LogFormatter` methods
- `tests/source_quality_test.py` — scans source files for banned markers
  (`todo`, `bug`, `fixme`, `hack`, case-insensitive)
- `examples/` directory with four runnable scripts: `basic_logging.py`,
  `timestamp_formats.py`, `relative_time.py`, `verbosity.py`

### Changed

- `getLogger()` now always returns a `KamiLogger` instance; upgrades
  pre-existing loggers via `__class__` assignment
- `add_verbose_arguments`, `calc_verbosity`, `set_logging_level_by_verbosity`
  now exported via `__all__`
- log record is copied before formatting to prevent mutation of the shared
  record across handlers
- `_PADDED_LEVELNAME_MAP` moved to module level
- improved help message for verbosity arguments

[1.3.0]: https://github.com/kami-lel/kamilog/compare/v1.2.0...v1.3.0













## [1.2.0] - 2025-10-01

### Added

- function related to verbosity and logging levels

  - related tests

[1.2.0]: https://github.com/kami-lel/kamilog/compare/v1.1.0...v1.2.0













## [1.1.0] - 2025-09-10

### Added

- Installation as Module feature

[1.1.0]: https://github.com/kami-lel/kamilog/compare/v1.0.0...v1.1.0

















## [1.0.0] - 2025-09-10

### Added

- basic function implemented in `kamilog.py`

[1.0.0]: https://github.com/kami-lel/kamilog/releases/tag/v1.0.0













[^format]: CHANGELOG format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); Version scheme adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).