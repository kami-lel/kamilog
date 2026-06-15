# kamilog CHANGELOG

[^format]
















## [Unreleased]

### Added

- Two new custom log levels:
  - `SUCC` (22) — task or operation succeeded; `.succ()` method
  - `DONE` (25) — task or operation completed; `.done()` method
- New example script `logger_names_and_timestamps.py` demonstrating logger names,
  timestamps, and multiple messages in one session

### Changed

- **Log output format**: removed brackets around level names
  - was: `[DEBUG] source: message`
  - now: `DEBUG source: message`
- **Timestamp defaults to opt-in**: timestamps now default to `None` (no timestamp shown);
  previously defaulted to time-only format. Pass `datefmt=` or `relative_to=` to enable.
- **Message separator**: changed from tab to single space after source/colon
  - was: `DEBUG source:\tmessage`
  - now: `DEBUG source: message`
- **Source-less logging**: no space before colon when logger has no name
  - was: `DEBUG :`
  - now: `DEBUG:`
- **PASS level number**: reduced from 25 to 21 to accommodate new levels
  - `PASS` (21) — hook or test case passed
  - `SUCC` (22) — task or operation succeeded
  - `DONE` (25) — task or operation completed
- **ANSI color scheme**: refined level-to-color mapping
  - `PASS` (21): bold bright green (`\033[1;92m`)
  - `SUCC` (22): bold green (`\033[1;32m`)
  - `DONE` (25): bright yellow (`\033[93m`)
  - `WARN` (30): yellow (`\033[33m`)
  - `CRIT` (50): bold bright yellow (`\033[1;93m`)
- Example scripts updated: cleaner output with styled print headers, root logger
  (no source names), section demonstrations
- Documentation (README, AGENTS, docs/) updated to reflect new log levels, format,
  timestamp behavior, and color scheme

### Deprecated

### Removed

### Fixed

- Fixed spacing between timestamp and level when timestamp is present

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