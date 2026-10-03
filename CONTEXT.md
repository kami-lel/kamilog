# kamilog CONTEXT

## Project Overview

kamilog is a lightweight Python logging utility wrapping the stdlib `logging` module. It adds custom log levels, combinable ANSI color, badges, flexible timestamps, and a diff-only filter that compresses repeated lines. The one logging entry point, `kamilog.getLogger()`, returns a drop-in replacement for `logging.getLogger()`. It installs as a package: no build step, no runtime dependency beyond the stdlib.

Repository: <https://github.com/kami-lel/kamilog>

## Repository Layout

| path | holds |
| --- | --- |
| `kamilog/__init__.py` | `__version__`, the explicit `__all__`, and every public name imported from its module |
| `kamilog/levels.py` | `_CustomLogLevel`, level constants |
| `kamilog/ansi.py` | `AnsiStyle`, `AnsiRenderer` |
| `kamilog/badges.py` | `_NATIVE_BADGES`, `_normalize_badges` |
| `kamilog/tab_align.py` | tab-stop helpers, `_TabAlignedLine` |
| `kamilog/formatter.py` | `DATEFMT_*`, `_LogFormatEngine`, `_LogFormatter` |
| `kamilog/diff_only.py` | `_DiffOnlyEngine`, `_DiffOnlyMsgFilter` |
| `kamilog/logger.py` | `KamiLogger`, `getLogger` |
| `kamilog/verbosity.py` | verbosity helpers and level mapping |
| `kamilog/banner.py` | comment banner generators |
| `kamilog/cli.py`, `kamilog/__main__.py` | CLI parsers and entry point, `python -m kamilog` |
| `tests/<area>/` | one suite per area (`v`, `cb`, `ansi`, `lf`, `badge`, `logger`, `dof`, `tal`, `cli`); `demo/` subfolders hold golden-output tests for `examples/` |
| `examples/` | runnable demos per feature |
| `docs/` | user guides, one per topic; the README and `AGENTS.md` link them |
| `scripts/kamilog_shim.sh` | bash `kamilog()` fallback, meant to be copied into a caller's script |

## Architecture

### Custom Levels

`_CustomLogLevel` is a private `IntEnum` holding every custom level: the int value plus a 5-char padded display name (`.display`). Module-level aliases (`ENTER`, ~~) keep the public API flat. `KamiLogger` carries one convenience method per custom level (`pass_` carries the trailing underscore).

Full progression: `DEBUG`(10) → `ENTER`(15) → `SKIP`(16) → `SUCC`(17) → `INFO`(20) → `PASS`(21) → `NOTE`(23) → `TIP`(24) → `DONE`(25) → `HINT`(26) → `IMPORTANT`(27) → `WARNING`(30) → `CAUTION`(31) → `ERROR`(40) → `FAIL`(45) → `CRITICAL`(50).

### ANSI Color

- `AnsiStyle`: public combinable `Flag` of foreground, background, and attribute bits; `parse(raw)` reads comma-separated names and raises `ValueError` on an unknown one
- `AnsiRenderer`: detects TTY once at construction; without a TTY, or with `is_disabled=True`, every method returns its input unchanged. Owned by `_LogFormatter` as `palette`, so the diff-only engine shares its TTY state
- `color_triage_tag()`: one hue per tag type across its three loudness tiers, contrast rising with loudness; `ValueError` for any other string

### `getLogger()`

Each call:

1. retrieves or creates a stdlib logger and upgrades it to `KamiLogger` by `__class__` assignment
2. attaches a `_DiffOnlyMsgFilter` if absent
3. adds stdout (`< WARNING`) and stderr (`>= WARNING`) handlers if none exist, unless `disable_console=True`
4. adds a color-disabled `FileHandler` with no level split when `filename` is set, once per resolved path

`datefmt` defaults to the private sentinel `_DATEFMT_AUTO`, resolved once per call: console gets no timestamp, the file gets `DATEFMT_DATETIME_MS`. An explicit value, `None` included, applies to console and file alike, as does `relative_to`. The diff-only filter measures the console prefix, so its tab stops follow the console format. `enable_propagate` defaults off so records never double-print through an ancestor's handlers.

### Badges

Labels for the mode of the whole run (`dry`, `force`, `auto`, ~~); kamilog only records and displays them.

- `_NATIVE_BADGES` maps each native label to `(AnsiStyle hue, priority)`, higher priority printing first; any other label is custom: magenta, priority 0
- `_normalize_badges` dedupes and orders by descending priority, customs keeping given order
- `set_persistent_badges()` / `clear_persistent_badges()` replace or unset the persistent set, stored per logger; there is no add or remove of one label
- `_log` override merges per-call `badges` with the persistent set (`is_inheriting_badges=False` hides it for one record), stamps `record.badges`, and forwards with `stacklevel + 1` so `funcName` and `lineno` point at the caller

### Formatting

- `_LogFormatEngine` holds the formatting logic, independent of `logging.Formatter`; all color routes through the `AnsiRenderer`. `count_prefix_chars` gives the printable width before the message. With badges it is a display column: badges follow the level and the source starts on the first tab stop strictly after them
- a line without badges is byte-identical to the pre-badge format; `record.badges` is read with a default so plain `logging` records still work
- `_LogFormatter` is the thin `logging.Formatter` adapter exposing `palette` and `engine`; it appends `exc_info`/`stack_info` itself

### Diff-Only Compression

`_DiffOnlyMsgFilter`, attached by `getLogger()`, replaces characters shared across the last `threshold` (default 3) messages with `〃` markers. It wraps a `_DiffOnlyEngine`, absent when `disable_diff_only_compression=True`. `getLogger()` gives it a dedicated stdout `_LogFormatter` so its palette matches the stdout handler.

- the engine keeps the raw, uncompressed text in `_history`, so decisions never rest on prior compressed output. The first `threshold` messages pass through (warmup)
- per line index *k*, `_common` holds the characters shared by line *k* of every history message; a line missing from any history message never compresses. Only line 1 starts at the prefix width, later lines at column 0
- each common run cuts on a word boundary (`0-9A-Za-z-_` are word characters), keeping the changing token's stem; without one within 2 tab stops it falls back to the tab-aligned floor, so compression never vanishes on long unbroken tokens
- the replaceable span splits through `_TabAlignedLine` (8-wide tab-stop blocks; embedded tabs expand to spaces first). Full blocks compress to one `〃\t`, a short gap renders as `〃` plus padding, and a leader of `_LEADER_MARKER_MIN` (4) columns or more gets its own marker, a shorter one a bare `\t`. Runs too short for a full block print untouched
- long-line rule: a physical line wider than `_LONG_LINE_COLS` (100) rendered uncompressed uses space-separated `〃 ` dittos and drops tab jumps and padding; decided per line, so one message may mix both forms. The result is narrower but not guaranteed to fit 100

### Comment Banners

`gen_comment_banner_{centered,left_just,right_just}` share the dispatcher `_gen_comment_banner_generic`; `gen_comment_banner_zero` (CB0) boxes multiple lines. All return a `str` and never print. Padding is a single printable non-space character or an int 1~5 (`#`, `=`, `*`, `+`, `-`); fill is grey, content and the two-space separators uncolored. Validation raises `ValueError`. `horizontal_offset` applies to centered mode only. Callers repeating calls on one stream should pass one `renderer=`.

### Verbosity

`add_verbose_arguments` adds step flags (`--verbose`/`--quiet`, ±1 per use) and extremity flags (`--max-verbose`/`--max-quiet`, ±`_EXTREME_VERBOSITY`), all four long options always, short letters chosen by `step_flags` / `extremity_flags`. `calc_verbosity` folds a namespace's counts into a base; `calc_logging_level` maps the result to a level, default `DONE` (25), pinned to `DEBUG` at ≥ 3 and `CRITICAL` at ≤ -3.

### Command-Line Interface

The `kamilog` console script (`[project.scripts]`) has subcommands `comment_banner`/`cb`, `comment_banner_zero`/`cb0`, `color`/`c`, `color-grey`, and `logger`/`l`. Content comes from stdin (Unix pipe pattern), so positionals are formatting-only. Run `kamilog <subcommand> -h` for arguments.

- shared flags come from layered `add_help=False` parents: `_common_parser` (`-n`/`-N`) → `_no_color_parser` (`-C`) → `_line_width_parser` (`-w`). `color` and `color-grey` inherit only `_common_parser`, since disabling color contradicts their purpose
- every subcommand attaches through a `_register_*_parser` call at the bottom of `cli.py`; only `_cli_parser` and `_cli_subparser` are module-level
- `_calc_line_end` decides the trailing newline: the kept stdin newline plus an appended one for `-n`; none appended for `-N`; exactly one for auto. `logger` sets it as the handlers' `terminator` just before the last record, so earlier records keep their breaks
- `logger` resolves `LEVEL` and `--time-format` through `_LOGGER_LEVEL_MAP` / `_LOGGER_TIME_FORMAT_MAP`; `notset` is excluded since a record at that level never emits. `--time-format` defaults to `no-time`; `--verbosity` sets the base the `-v`/`-q` counts offset from (default 3)

## Known Gaps

- CLI subcommands' original arguments (mode, padding, width, stderr routing, level resolution, verbosity) have no dedicated tests; the shared `-n`/`-N`/`-C` flags do (`tests/cli/`)
