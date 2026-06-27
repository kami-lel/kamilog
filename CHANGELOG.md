# kamilog CHANGELOG

[^format]

<!-- todo smart time print -->















## [Unreleased]

### Added

### Changed

- `SUCC` custom log level renumbered 22 → 15, now sits between `SKIP` (12) and `INFO` (20)
- ANSI color scheme revised: `DEBUG`/`ENTER` use cyan/bright cyan (`\033[36m`/`\033[96m`); `SKIP`/`INFO` use blue/bright blue (`\033[34m`/`\033[94m`); `SUCC` uses green (`\033[32m`); `PASS` uses bright green (`\033[92m`)
- `docs/usage_doc.md` "Custom Log Levels" section rewritten: all levels (native and custom) consolidated into one reference table with level name, number, function, color, and ANSI code columns; duplicate color table removed from "ANSI Color Output"
- `docs/usage_doc.md` "Logging" section example revised to show custom levels alongside native ones and exception handling in a single code block
- `examples/all_levels.py` reordered `succ()` call to match updated level 15 position

### Deprecated

### Removed

### Fixed

### Security

[unreleased]: https://github.com/kami-lel/kamilog/compare/v1.5.0...dev













## [1.5.0] - 2026-06-27

### Added

- `_DiffOnlyMsgFilter`: auto-attached to every logger by `getLogger()`; compresses character runs shared across the last 3 messages into `〃\t` markers (one per 8 chars), preserving 2 original chars at each end for visual context.
- `examples/diff_only_filter.py`: runnable demo of diff-only filtering across three scenarios — sensor polling, batch file processing, and pattern break/recovery.
- `CONTEXT.md`: descriptive architecture reference covering repository layout, core classes (`_CustomLogLevel`, `KamiLogger`, `_LogFormatter`, `_DiffOnlyMsgFilter`), public API surface, and known limitations.

### Changed

- Custom log levels (`ENTER`, `SKIP`, `PASS`, `SUCC`, `DONE`, `FAIL`) consolidated into `_CustomLogLevel(IntEnum)`; each member carries the numeric level value and a padded 5-char display name (`.display`). Public module-level aliases are unchanged and remain int-compatible.
- `AGENTS.md` restructured to prescriptive-only content (commands, conventions, constraints); descriptive content moved to `CONTEXT.md`.

[1.5.0]: https://github.com/kami-lel/kamilog/compare/v1.4.2...v1.5.0













## [1.4.2] - 2026-06-16

### Changed

ANSI formatting (styling):
- Level keywords: now displayed in bold with their assigned colors
- Timestamp: bright black (grey) color
- Source name: bright black (grey) color
- Colon separator: bright black (grey) color

Documentation:
- Updated `docs/usage_doc.md` to document formatting colors and styles

[1.4.2]: https://github.com/kami-lel/kamilog/compare/v1.4.1...v1.4.2













## [1.4.1] - 2026-06-16

### Changed

Log level formatting:
- Level names now include periods: `SUCC.`, `WARN.`, `CRIT.`

### Fixed

Documentation:
- Restored missing README title
- Updated usage examples to match level name formatting
- Added custom log level output examples in usage documentation

[1.4.1]: https://github.com/kami-lel/kamilog/compare/v1.4.0...v1.4.1











## [1.4.0] - 2026-06-16

### Added

Custom log levels:
- `SUCC` (22) — task or operation succeeded; `.succ()` method
- `DONE` (25) — task or operation completed; `.done()` method

Examples:
- `logger_names_and_timestamps.py` — demonstrates logger names, timestamps, and multiple messages

### Changed

Log output format:
- Removed brackets around level names: `[DEBUG]` → `DEBUG`
- Changed message separator from tab to single space: `source:\tmessage` → `source: message`
- Removed space before colon when logger has no name: `DEBUG :` → `DEBUG:`
- Timestamps default to opt-in (`None`) instead of time-only format

Log levels:
- `PASS` level reduced from 25 → 21 to accommodate new levels
- Complete level progression: `PASS` (21), `SUCC` (22), `DONE` (25)

ANSI color scheme (refined):
- `PASS` (21): bold bright green
- `SUCC` (22): bold green
- `DONE` (25): bright yellow
- `WARN` (30): yellow
- `CRIT` (50): bold bright yellow

CLI verbosity mapping (restructured):
- `-vv` or more → `DEBUG` (10)
- `-v` → `INFO` (20)
- no flags → `DONE` (25) *(was `WARNING` 30)*
- `-q` → `WARNING` (30) *(was suppressed)*
- `-qq` → `ERROR` (40) *(new)*
- `-qqq` or more → `CRITICAL` (50) *(new)*

Examples & documentation:
- Example scripts: cleaner output with styled print headers, root logger (no source names)
- `examples/verbosity.py`: comprehensive usage examples for all flag combinations
- Updated README, AGENTS, docs/ to reflect all changes

### Fixed

- Fixed spacing between timestamp and level when timestamp is present

[1.4.0]: https://github.com/kami-lel/kamilog/compare/v1.3.1...v1.4.0















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