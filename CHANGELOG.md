# kamilog CHANGELOG

<!--
todo smart time print
todo cli logger: implement relative time
todo cli logger: allow to use already set up logger
bug using different logger to print & diff only can produce confusing result
-->

[^format]















## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

[unreleased]: https://github.com/kami-lel/kamilog/compare/v2.8.0...dev













## [2.8.0] - 2026-07-17

### Added

- file logging — `getLogger` can now write to a log file, with an option for a file-only logger that mutes the console
- `calc_verbosity` and `calc_logging_level` — the verbosity-to-level conversion is now public
- `--max-verbose`/`--max-quiet` CLI flags — jump straight to the highest or lowest verbosity, and choose which short flags bind to the stepwise and extremity behaviors

[2.8.0]: https://github.com/kami-lel/kamilog/compare/v2.7.0...v2.8.0













## [2.7.0] - 2026-07-11

### Added

- `horizontal_offset` parameter on `gen_comment_banner_centered`, nudging the centered content left or right by a given number of columns; raises `ValueError` when the offset pushes either fill side below zero
- `examples/cb/cb-offset-demo.py`, showing a prefixed banner kept aligned with a bare one via `horizontal_offset`

[2.7.0]: https://github.com/kami-lel/kamilog/compare/v2.6.0...v2.7.0













## [2.6.0] - 2026-07-10

### Added

New custom log levels, each with a matching method:

- `NOTE` (23) — `.note()` — general aside worth noting
- `TIP` (24) — `.tip()` — actionable suggestion
- `HINT` (26) — `.hint()` — subtle, barely-there cue
- `IMPORTANT` (27) — `.important()` — emphasized information that should stand out
- `CAUTION` (31) — `.caution()` — risk of a negative outcome, heed carefully

### Changed

- `docs/usage_doc.md` — Custom Log Levels table documents the five new levels
- `examples/logger/logger-all_levels_demo.py` — demonstrates all sixteen log levels
- ANSI colors for `NOTE`, `TIP`, `HINT`, and `IMPORTANT` revamped for clearer visual distinction, unifying the log color palette

### Fixed

- `tests/source_quality_test.py` — banned-marker scan no longer flags `todo`/`bug`/`fixme`/`hack` occurrences inside string literals

[2.6.0]: https://github.com/kami-lel/kamilog/compare/v2.5.0...v2.6.0













## [2.5.0] - 2026-07-09

### Added

- `AnsiStyle` — foreground/background colors and text attributes are now combinable `Flag` members
  (mix with `|`, e.g. `AnsiStyle.BOLD | AnsiStyle.RED | AnsiStyle.BG_YELLOW`),
  replacing the old fixed `AnsiColor` enum
- New `AnsiStyle` colors: `BLACK`, `WHITE`, `BRIGHT_WHITE`, and background counterparts for every foreground hue (`BG_RED`, `BG_BRIGHT_CYAN`, etc.)
- `AnsiRenderer.color_triage_tag(triage_tag)`:
  colors a triage-tag string by tag type, with contrast escalating for louder case tiers
- `examples/ansi/ansi-tt-demo.py`: demonstrates `color_triage_tag` across all 12 triage-tag variants

### Changed

- `AnsiRenderer.color(text, style)` now takes a single combined `AnsiStyle`
  value instead of a color plus a `use_bold` flag
- moved `ansi-style-demo.py` into `examples/ansi/`

[2.5.0]: https://github.com/kami-lel/kamilog/compare/v2.4.0...v2.5.0













## [2.4.0] - 2026-07-08

### Added

New `logger` CLI subcommand (alias `l`) — pipe lines into stdin and log each
one at a chosen `LEVEL`, gated by a verbosity threshold:

- run it as `python kamilog/kamilog.py logger LEVEL`; each stdin line becomes
  one log record
- `--verbosity` — base verbosity the subcommand's `-v`/`-q` counts adjust
  from (default `3`)
- `-t`/`--time-format` — timestamp style: `time`, `time-ms`, `datetime`,
  `datetime-ms`, or `no-time` (default `time`)
- `-C`/`--no-color` — force plain output, disabling ANSI color even on a TTY
- `-D`/`--no-diff-only` — emit every line in full, skipping diff-only
  compression

Two new `getLogger()` toggles, both propagating through every handler and the
diff-only filter:

- `disable_color` — suppress ANSI color regardless of TTY state
- `disable_diff_only_compression` — skip the compression engine so records
  pass through untouched

Other additions:

- `AnsiRenderer` — new `is_disabled` keyword that turns color off
  unconditionally, regardless of the stream's TTY state
- golden-output tests for every `examples/` demo script, asserting exact
  captured stdout/stderr so future changes can't silently alter demo output
  (`tests/cb/demo/`, `tests/dof/demo/`, `tests/logger/demo/`)
- `logger-diff_only_stress_demo.py` — new "embedded tab" scenario, showing
  compression when message content already contains a literal `\t`

### Changed

CLI internals (no public-surface change):

- the root parser and subparser are now private (`_cli_parser`,
  `_cli_subparser`), so the module's public surface matches `__all__` exactly
- every subcommand is built by a `_register_*_parser(cli_subparser)` function
  (`comment_banner`, `comment_banner_zero`, `logger`) instead of a
  module-level parser object

Diff-only compression:

- `_DiffOnlyEngine._compress` now splits the replaceable span into
  `_TabAlignedLine` blocks — an internal `list` subclass that breaks a line
  into 8-wide tab-stop blocks and expands any literal `\t` before splitting —
  instead of computing boundaries inline; `_COMPRESSION_BLOCK_SIZE` gives way
  to `_TabAlignedLine.TAB_SIZE`

### Fixed

- CLI help and usage now show the program name as `kamilog`, not `__main__`
- diff-only compression restored to a character-precise cut, preserving word
  boundaries — a lone `=` between fields no longer gets swallowed by the
  compressed run
- message content containing a literal `\t` no longer misaligns diff-only
  compression; embedded tabs are expanded before the block split













## [2.3.1] - 2026-07-06

### Changed

- `set_logging_level_by_namespace()` — new `verbosity=0` kwarg sets a base
  level that the namespace's `-v`/`-q` counts offset from, instead of always
  starting from zero
- `docs/usage_doc.md` and `CONTEXT.md` — documented the `verbosity` kwarg













## [2.3.0] - 2026-07-06

### Added

- `set_logging_level_by_verbosity()` — set a logger's level directly from a
  verbosity integer, no parsed `argparse` namespace needed

### Changed

Verbosity API:

- `set_logging_level_by_verbosity()` renamed to
  `set_logging_level_by_namespace()`; the old name now takes a verbosity
  integer (see Added above)

Timestamps:

- timestamps are now shown by default: `getLogger()` defaults `datefmt`
  to `DATEFMT_TIME` (`HH:MM:SS`); pass `datefmt=None` to disable them

Diff-only compression:

- compressed runs now end at a word boundary, so a changing token keeps
  its full word intact (e.g. `/batch_002.csv`, not a mid-word fragment)
- long unbroken tokens (hashes, URLs) without a nearby boundary fall back
  to a tab-aligned cut, so compression never vanishes
- `_DiffOnlyMsgFilter`/`_DiffOnlyEngine` parameter `window` renamed to
  `threshold`

Documentation:

- "Verbosity and Logging Level" usage doc section reorganized into
  subheadings: CLI Flags, Verbosity Integer, Verbosity-to-Level Mapping

### Fixed

- Diff-only compression no longer leaks a fragment of common text between
  the last marker and the cut
- Verbosity tests brought in line with the v2.2.0 level mapping
  (`-vv` → `ENTER`); the full suite passes again

> [!WARNING]
> Two breaking changes: `set_logging_level_by_verbosity(namespace)` is now
> `set_logging_level_by_namespace(namespace)` — the old name takes an
> integer instead — and loggers print `HH:MM:SS` timestamps by default;
> pass `datefmt=None` to restore the previous silent output.













## [2.2.0] - 2026-07-02

### Changed

- Reordered custom log levels: `ENTER` (15), `SKIP` (16), `SUCC` (17) — placing structural flow markers (`ENTER`/`SKIP`) before success indicators (`SUCC`), closer to `DEBUG` and earlier in the verbosity hierarchy
- Verbosity flag `-vv` now maps to `ENTER` (15) instead of `SUCC` — making `-vv` the threshold for structural tracking
- Updated all examples and documentation to reflect new level ordering













## [2.1.1] - 2026-07-02

### Added

- `examples/cb/cb-number-demo.py` — numeric padding shortcuts (1-5) demo

### Changed

- simplified usage tips in `docs/usage_doc.md` — condensed log-level guidance, consolidated testing tips, reordered DONE
- reorganized comment-banner demos under `examples/cb/` — renamed to `cb-demo.py` and `cb-zero_demo.py`

### Fixed

- CLI `cb` subcommand padding conversion — numeric arguments (1-5) now correctly convert to integer for preset characters

[2.4.0]: https://github.com/kami-lel/kamilog/compare/v2.3.1...v2.4.0
[2.3.1]: https://github.com/kami-lel/kamilog/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/kami-lel/kamilog/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/kami-lel/kamilog/compare/v2.1.1...v2.2.0
[2.1.1]: https://github.com/kami-lel/kamilog/compare/v2.1.0...v2.1.1













## [2.1.0] - 2026-07-02

### Added

- `comment_banner_zero()` and CLI subcommand `comment_banner_zero` (alias `cb0`) — a multi-line
  boxed comment banner (CB0), framed top and bottom by `#` rulers
- Comment-banner functions accept an integer `padding` shorthand (1-5) for common fill
  characters: `#`, `=`, `*`, `+`, `-`
- Example demo: `examples/comment_banner_zero_demo.py`

### Changed

- Renamed the line-padding API to comment-banner: `gen_line_padding_*` → `gen_comment_banner_*`,
  CLI subcommand `line_padding` (`lp`) → `comment_banner` (`cb`)
- Reorganized tests, examples, and docs to match the new naming
- `cb` and `cb0` now read their text content from stdin instead of a positional argument,
  following the Unix pipe pattern
- Clearer `--help` output for `cb`/`cb0`, with usage examples and a better `PADDING` description

> [!WARNING]
> This release renames the line-padding API to comment-banner, and switches the `cb`/`cb0` CLI
> subcommands to read content from stdin. Update callers to use `gen_comment_banner_*` and pipe
> input, e.g. `echo 'title' | python kamilog/kamilog.py cb c '='`.

[2.1.0]: https://github.com/kami-lel/kamilog/compare/v2.0.0...v2.1.0




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