# kamilog CHANGELOG

[^format]















## [Unreleased]

### Changed

- API renaming: `gen_line_padding_*` functions renamed to `gen_comment_banner_*`
  - `gen_line_padding_centered` → `gen_comment_banner_centered`
  - `gen_line_padding_left_just` → `gen_comment_banner_left_just`
  - `gen_line_padding_right_just` → `gen_comment_banner_right_just`
  - Internal `_gen_line_padding_generic()` → `_gen_comment_banner_generic()`
- CLI subcommand renamed: `line_padding` → `comment_banner` with alias `cb` (replacing `lp`)
- Test directory reorganized: `tests/lp/` → `tests/cb/`; test files renamed from `lp-*_test.py` → `cb-*_test.py`
- Example file renamed: `examples/line_padding_demo.py` → `examples/comment_banner_demo.py`
- Documentation updated throughout to reflect new terminology

> [!WARNING]
> This release renames the line-padding API to comment-banner. Update callers to use the
> `gen_comment_banner_*` function names and CLI subcommand `comment_banner` (or alias `cb`).

### Added

- Comment-banner functions now accept integer `padding` (1-5) as shorthand for common fill characters
  - `1` → `#`, `2` → `=`, `3` → `*`, `4` → `+`, `5` → `-`
  - Example: `gen_comment_banner_centered("title", 2)` equivalent to `gen_comment_banner_centered("title", "=")`
- `gen_comment_banner_zero(lines, *, line_width=80, file=sys.stdout, renderer=None)` — multi-line boxed comment banner (CB0)
  - wraps each line with grey-colored `# ` prefix
  - frames with top and bottom grey-colored `#` rulers at full `line_width`
  - returns formatted banner as string
- CLI subcommand `comment_banner_zero` (alias: `cb0`) with support for multiple lines
  - Usage: `python kamilog/kamilog.py cb0 "Line 1" "Line 2" -w 40`
- Example demo: `examples/comment_banner_zero_demo.py` showcasing CB0 usage patterns

### Deprecated

### Removed

### Fixed

### Security

[unreleased]: https://github.com/kami-lel/kamilog/compare/v2.0.0...dev




## [2.0.0] - 2026-07-02

### Changed

- `print_line_padding_centered`, `print_line_padding_left_just`, `print_line_padding_right_just` renamed to `gen_line_padding_centered`, `gen_line_padding_left_just`, `gen_line_padding_right_just`; each now returns the padded line as a `str` instead of printing it
- CLI `line_padding` subcommand (alias `lp`) updated internally to print the returned line; command-line behavior is unchanged

### Removed

- `end` and `flush` keyword arguments removed from all line-padding functions

> [!WARNING]
> This release breaks the line-padding API. Update callers to use the
> `gen_line_padding_*` names and print the returned string yourself.

[2.0.0]: https://github.com/kami-lel/kamilog/compare/v1.8.0...v2.0.0













## [1.8.0] - 2026-07-02

### Added

- CLI (`python kamilog/kamilog.py`) with a `line_padding` subcommand (alias: `lp`)
- Mode argument accepts short (`c`, `l`, `r`) or long (`center`, `left`, `right`) forms
- `-w, --line-width` option (default 80) and `-e, --stderr` flag for the CLI

### Changed

- Docstrings condensed to Sphinx/reStructuredText style throughout the module
- `_print_line_padding_generic()` now takes string modes (`"c"`, `"l"`, `"r"`) instead of integers
- README reorganized into emoji-labeled feature sections
- docs/usage_doc.md: refined Custom Log Levels table, added usage tips

### Fixed

- `_print_line_padding_generic()` mode comparison corrected to match its string-based modes

[1.8.0]: https://github.com/kami-lel/kamilog/compare/v1.7.0...v1.8.0













## [1.7.0] - 2026-07-01

### Added

- `AnsiColor` — public `Enum` of ANSI escape code constants keyed by color name
- `AnsiRenderer` — public TTY-aware color renderer promoted from `_AnsiPalette`; exposes `color(text, color, *, use_bold=False)`, `color_level(text, levelno)`, and `color_grey(text)`
- `print_line_padding_centered`, `print_line_padding_left_just`, `print_line_padding_right_just` — fixed-width line-padding functions; all accept a `renderer` kwarg, return the `AnsiRenderer` used, and color the padding fill grey on TTY output; raise `ValueError` on invalid `content` or `padding`

### Changed

- `kamilog/__init__.py` — simplified to wildcard re-export (`from .kamilog import *`); `__all__` is now dynamic, matching `kamilog.py` exactly
- `examples/` — reorganized into `examples/logger/` subdirectory; all scripts renamed to `*_demo.py`; timestamp demos consolidated into `logger-timestamps_demo.py`; `verbosity_demo.py` and `line_padding_demo.py` added

### Removed

- `_AnsiPalette` — replaced by public `AnsiRenderer`

### Fixed

- `print_line_padding_left_just` and `print_line_padding_right_just` — output was two characters short of `line_width`; fill calculation incorrectly subtracted both separators instead of one

[1.7.0]: https://github.com/kami-lel/kamilog/compare/v1.6.2...v1.7.0













## [1.6.2] - 2026-06-29

### Added

- `pyproject.toml`: modern PEP 518 build configuration with dynamic version and author resolution

### Changed

- **docs**: reorganized `install_guide.md` with clearer structure (Package Install vs Copy Install sections), numbered steps, inline path diagrams, and visual improvements for readability

### Removed

- `setup.py`: minimal shim removed in favor of `pyproject.toml`
- `setup.cfg`: consolidated into `pyproject.toml`

[1.6.2]: https://github.com/kami-lel/kamilog/compare/v1.6.1...v1.6.2














## [1.6.1] - 2026-06-28

### Added

- `_AnsiPalette`: internal class centralizing ANSI color detection and application; exposes `color_level(text, levelno)` and `color_grey(text)`; replaces module-level `_ANSI_*` constants

### Changed

- `_LogFormatter` now accepts `stream` as first positional argument instead of `use_color: bool`; `palette` and `engine` promoted to plain public attributes
- `_LogFormatEngine` now accepts a `_AnsiPalette` instance instead of `use_color: bool`; all color output is routed through the palette

### Fixed

- `_DiffOnlyMsgFilter` compression markers (`〃\t`) now appear in grey when output is a TTY; the formatter for the filter was constructed without a stream, so `_AnsiPalette` disabled color unconditionally

[1.6.1]: https://github.com/kami-lel/kamilog/compare/v1.6.0...v1.6.1














## [1.6.0] - 2026-06-28

### Added

- `_LogFormatEngine`: internal class holding all log-line formatting logic, independent of `logging.Formatter`; exposes `count_prefix_chars`, `format_time`, and `build_line`
- `_LogFormatter.engine` property: public access to the internal `_LogFormatEngine` instance
- `_DiffOnlyEngine._COMPRESSION_BLOCK_SIZE` (8), `_PRESERVED_TRAILING_CHARS` (2), and `_COMPRESSION_MARKER` (`"〃\t"`) private class constants replacing inline magic values
- `examples/diff_only_stress.py`: dual-logger stress test contrasting short and long message compression

### Changed

- `SUCC` log level renumbered 22 → 15, placing it between `SKIP` (12) and `INFO` (20)
- ANSI color scheme revised: `DEBUG`/`ENTER` cyan/bright cyan; `SKIP`/`INFO` blue/bright blue; `SUCC` green; `PASS` bright green
- verbosity mapping extended: `-vv` now maps to `SUCC` (15); `-vvv` or more maps to `DEBUG` (10)
- `_LogFormatter` refactored as a thin `logging.Formatter` adapter; all formatting logic moved to `_LogFormatEngine`
- `_DiffOnlyEngine` and `_DiffOnlyMsgFilter` now accept `formatter` directly at construction instead of resolving it lazily from a logger's handlers
- `_DiffOnlyMsgFilter` tab placement aligns each `〃\t` to 8-column boundaries measured from the rendered line start, accounting for prefix length via `count_prefix_chars`
- `docs/usage_doc.md` "Custom Log Levels" section consolidated into a single reference table covering all levels; duplicate color table removed
- `examples/diff_only_filter.py` renamed to `examples/diff_only.py`

### Removed

- `calc_verbosity()` removed from public API; verbosity-to-level conversion is now handled internally

### Fixed

- `_DiffOnlyMsgFilter` `〃\t` markers now align to correct tab stops regardless of prefix length; the previous heuristic ignored the rendered prefix width

[1.6.0]: https://github.com/kami-lel/kamilog/compare/v1.5.0...v1.6.0













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