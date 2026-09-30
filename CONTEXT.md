# kamilog CONTEXT

*Last updated: 2026-09-30 - v2.9.4-alpha*

## Project Overview

kamilog is a lightweight Python logging utility that wraps the stdlib `logging` module. It adds structured output, custom log levels, combinable ANSI color styling, flexible timestamp options, and a diff-only message filter that compresses repeated log lines. The public API is a single entry point — `kamilog.getLogger()` — that returns a fully configured logger as a drop-in replacement for `logging.getLogger()`.

Repository: <https://github.com/kami-lel/kamilog>

## Repository Layout

```
kamilog/
├── kamilog/
│   ├── __init__.py          # re-exports all public symbols from kamilog.py
│   └── kamilog.py           # entire implementation (~2265 lines)
├── tests/
│   ├── cb/                          # comment-banner test suite
│   │   ├── cb-centered_test.py
│   │   ├── cb-left_just_test.py
│   │   ├── cb-right_just_test.py
│   │   ├── cb-validation_test.py
│   │   └── demo/                    # golden-output tests for examples/cb/*
│   ├── v/                           # verbosity helper test suite
│   │   ├── v-add_verbose_arguments_test.py
│   │   ├── v-calc_verbosity_test.py
│   │   ├── v-calc_logging_level_test.py
│   │   ├── v-calc_logging_level_namespace_test.py
│   │   ├── v-set_logging_level_by_namespace_test.py
│   │   └── demo/                    # golden-output tests for examples/verbosity_demo.py
│   ├── ansi/                        # AnsiRenderer / TTY detection test suite
│   │   └── demo/                    # golden-output tests for examples/ansi/*
│   ├── badge/                       # badge table / normalizer / KamiLogger badge API
│   ├── lf/                          # _LogFormatter / _LogFormatEngine test suite (incl. badge display, color, prefix width)
│   ├── logger/                      # KamiLogger behavior test suite
│   │   └── demo/                    # golden-output tests for examples/logger/*
│   ├── dof/                         # _DiffOnlyEngine / _DiffOnlyMsgFilter test suite (incl. multi-line, long-line, badge interaction)
│   │   └── demo/                    # golden-output tests for examples/logger/*diff_only*
│   ├── tal/                         # _TabAlignedLine test suite
│   └── source_quality_test.py       # banned-marker scan (no TODO/FIXME/HACK/BUG)
├── examples/
│   ├── ansi/
│   │   ├── ansi-style-demo.py                # AnsiStyle flags and color combinations
│   │   └── ansi-tt-demo.py                   # color_triage_tag across all 12 triage tags
│   ├── cb/
│   │   ├── cb-demo.py                       # all three comment-banner functions with char padding
│   │   ├── cb-number-demo.py                # numeric padding shortcuts (1-5)
│   │   ├── cb-offset-demo.py               # centered horizontal_offset aligning a prefixed banner
│   │   └── cb-zero_demo.py                  # multi-line boxed banner (CB0)
│   ├── verbosity_demo.py                    # CLI -v/-q flags with custom levels
│   └── logger/
│       ├── logger-all_levels_demo.py        # all sixteen log levels with descriptions
│       ├── logger-timestamps_demo.py        # all four DATEFMT_* formats and relative_to
│       ├── logger-badge_demo.py             # badges, multi-line & long-line dittos
│       ├── logger-diff_only_demo.py         # _DiffOnlyMsgFilter compression walkthrough
│       └── logger-diff_only_stress_demo.py  # word-boundary, leader, and embedded-tab
│                                             # compression scenarios
├── docs/
│   ├── usage_doc.md         # public API reference with examples
│   └── install_guide.md     # installation methods
├── scripts/
│   └── kamilog_shim.sh       # bash `kamilog()` fallback wrapper, meant to be copy-pasted
│                             # or sourced into a caller's own script
├── pyproject.toml           # PEP 518 build config; package metadata with dynamic version/author;
│                             # dev dependency group (`pip install -e . --group dev`) adds pytest
├── CHANGELOG.md
└── README.md
```

## Architecture

The entire library lives in `kamilog/kamilog.py`. There is no build step and no external runtime dependency.

### `_CustomLogLevel`

Private `IntEnum` subclass that consolidates every custom log level in one place. Each member stores two values: the numeric level (the enum's int value, used wherever an int is expected) and a 5-char padded display name accessed via `.display`. The `.name` property yields the bare name string used in `logging.addLevelName()`.

| member | value | `.name` | `.display` |
| --- | --- | --- | --- |
| `ENTER` | 15 | `"ENTER"` | `"ENTER"` |
| `SKIP` | 16 | `"SKIP"` | `"SKIP "` |
| `SUCC` | 17 | `"SUCC"` | `"SUCC."` |
| `PASS` | 21 | `"PASS"` | `"PASS "` |
| `NOTE` | 23 | `"NOTE"` | `"NOTE "` |
| `TIP` | 24 | `"TIP"` | `"TIP  "` |
| `DONE` | 25 | `"DONE"` | `"DONE "` |
| `HINT` | 26 | `"HINT"` | `"HINT "` |
| `IMPORTANT` | 27 | `"IMPORTANT"` | `"IMPT."` |
| `CAUTION` | 31 | `"CAUTION"` | `"CAUT."` |
| `FAIL` | 45 | `"FAIL"` | `"FAIL "` |

Module-level aliases (`ENTER = _CustomLogLevel.ENTER`, etc.) keep the public API unchanged. `_PADDED_LEVELNAME_MAP` and `KamiLogger`'s log methods all reference `_CustomLogLevel` directly.

### `AnsiStyle`

Public combinable `Flag` enum of ANSI style bits — foreground, background, and text-attribute flags, combined with `|` (e.g. `AnsiStyle.BOLD | AnsiStyle.RED | AnsiStyle.BG_YELLOW`). Members carry no ANSI meaning themselves; `AnsiRenderer._ANSI_STYLE2CODE` maps each flag to its escape code.

| category | members |
| --- | --- |
| foreground hues | `RED`/`BRIGHT_RED`, `YELLOW`/`BRIGHT_YELLOW`, `GREEN`/`BRIGHT_GREEN`, `CYAN`/`BRIGHT_CYAN`, `BLUE`/`BRIGHT_BLUE`, `MAGENTA`/`BRIGHT_MAGENTA` |
| foreground neutrals | `BLACK`, `GREY`, `WHITE`, `BRIGHT_WHITE` |
| background | `BG_`-prefixed counterpart of every foreground member above |
| text attribute | `BOLD`, `UNDERLINE` |

- `parse(raw)` (classmethod) — parses a comma-separated list of member names (e.g. `"RED,BOLD"`) into one combined `AnsiStyle` value; raises `ValueError` on an unknown member name

### `AnsiRenderer`

Public class that centralizes ANSI color detection and application. Instantiated by `_LogFormatter` and exposed via its `palette` attribute; also reachable from `_DiffOnlyEngine` as `formatter.palette`.

- Detects TTY status once at construction via `stream.isatty()`; when `stream` is `None` or not a TTY, all methods return their input unchanged.
- `is_disabled=False` (keyword-only) forces color off unconditionally at construction, regardless of the stream's TTY state.
- `color(text, style)` — generic style applier; wraps `text` in the ANSI codes for every flag set in the combined `AnsiStyle` value.
- `color_level(text, levelno)` — wraps `text` in bold + per-level ANSI color via the internal `_LEVEL2ANSI_COLOR` map.
- `color_badge(text, badge)` — wraps `text` in the badge's hue from `_NATIVE_BADGES`; any other (custom) badge is grey.
- `color_grey(text)` — wraps `text` in grey; used for timestamps, source labels, and compression markers.
- `color_triage_tag(triage_tag)` — colors a triage-tag string (`BUG`/`Bug`/`bug`, `FIXME`/`Fixme`/`fixme`, `TODO`/`Todo`/`todo`, `HACK`/`Hack`/`hack`) via the internal `_TRIAGE_TAG2ANSI_STYLE` map. Each tag type keeps one hue across its three loudness tiers, with contrast (background presence/brightness, bold) escalating for louder tiers. Raises `ValueError` for any other string.

### `getLogger(name, *, datefmt, relative_to, disable_color, disable_diff_only_compression, filename, file_mode, disable_console, enable_propagate)`

The sole public entry point. Every call:

1. Retrieves or creates a stdlib logger and upgrades it to `KamiLogger` via `__class__` assignment.
2. Attaches a `_DiffOnlyMsgFilter` instance if one is not already present.
3. Adds stdout and stderr `StreamHandler`s (with `_LogFormatter`) if no handlers exist yet — stdout for `< WARNING`, stderr for `>= WARNING` — unless `disable_console=True`, which skips the pair entirely.
4. When `filename` is set, adds a `FileHandler` carrying a color-disabled `_LogFormatter` and no level split (all levels land in the one file), idempotently per resolved absolute path.

Keyword-only options propagate to those parts:

- `disable_color=False` — forwarded to every `_LogFormatter` (as `disable_color`) and on to `AnsiRenderer(is_disabled=…)`, so all handlers and the diff-only filter emit plain text regardless of TTY state.
- `disable_diff_only_compression=False` — forwarded to `_DiffOnlyMsgFilter`; when `True` the filter skips building its `_DiffOnlyEngine` and passes records through untouched.
- `filename=None` — path to a log file; when set, attaches the `FileHandler` described above with color always disabled (a file is never a TTY).
- `file_mode="a"` — open mode forwarded to `logging.FileHandler` (`"a"` append, `"w"` truncate).
- `disable_console=False` — when `True`, omits the stdout/stderr handlers, yielding a file-only logger.
- `enable_propagate=False` — sets `logger.propagate`; kept off by default so records never double-print through an ancestor logger's handlers, unlike stdlib's default-`True` behavior.

### `KamiLogger`

Subclasses `logging.Logger`. Adds eleven convenience methods mapping to the custom levels:

| method | level name | numeric |
| --- | --- | --- |
| `.enter()` | `ENTER` | 15 |
| `.skip()` | `SKIP` | 16 |
| `.succ()` | `SUCC` | 17 |
| `.pass_()` | `PASS` | 21 |
| `.note()` | `NOTE` | 23 |
| `.tip()` | `TIP` | 24 |
| `.done()` | `DONE` | 25 |
| `.hint()` | `HINT` | 26 |
| `.important()` | `IMPORTANT` | 27 |
| `.caution()` | `CAUTION` | 31 |
| `.fail()` | `FAIL` | 45 |

#### Badges

`KamiLogger` also carries badges: labels for the mode the whole run is in (`dry`, `force`, `auto` and the rest). kamilog only records and displays them.

- `_NATIVE_BADGES` — module-level table mapping each native label to `(AnsiStyle hue, priority)`; a higher priority prints earlier. Any label absent from it is a custom badge: grey, priority 0.
- `_normalize_badges(badges)` — private pure function: accepts `None`, a `str` or an iterable, drops duplicates and orders by descending priority (stable for ties; customs keep the order given). Returns a tuple.
- `set_badges(badges=None)` / `clear_badges()` — replace or unset the run-wide set, stored per logger in `_run_badges` (class default `()`). `set_badges()`, `None` and `[]` all unset it; there is no add or remove of one label.
- `_log(..., badges=None, inherit_badges=True)` — override that merges per-call badges with the run-wide set (`inherit_badges=False` hides the run-wide set for one record) and stamps the result on the record as `record.badges` through `extra`. It forwards to `super()._log` with `stacklevel + 1`, so `funcName` and `lineno` still point at the caller. Every level method and `log()` accept the kwargs through `**kwargs`.

The user-facing guide is [`docs/badge-doc.md`](docs/badge-doc.md); `OpAction` (`docs/op_action_design.md`) is not implemented.

The full level progression: `DEBUG`(10) → `ENTER`(15) → `SKIP`(16) → `SUCC`(17) → `INFO`(20) → `PASS`(21) → `NOTE`(23) → `TIP`(24) → `DONE`(25) → `HINT`(26) → `IMPORTANT`(27) → `WARNING`(30) → `CAUTION`(31) → `ERROR`(40) → `FAIL`(45) → `CRITICAL`(50).

### `_LogFormatEngine`

Holds all core formatting logic, independent of `logging.Formatter`. Instantiated by `_LogFormatter` and exposed via its `engine` attribute. Takes an `AnsiRenderer` instance at construction; all color output is routed through the palette.

Responsibilities:

- `count_prefix_chars(record)` — returns the printable character count before the message text for a given record. Accounts for the optional timestamp (relative: always 13 chars; datefmt: rendered `time.strftime` length), the 5-char padded level name, and the source name with colon. When the record carries badges the value is a display column, not a character count: the badges follow the timestamp and the level starts on the first tab stop strictly after the badges (`_next_tab_stop`), so a literal tab in the line spans several columns. ANSI escape codes are excluded. Uses `time.strftime` directly so there is no dependency on `Formatter`.
- `format_time(record, datefmt)` — produces the optionally colored timestamp string, or an empty string when disabled.
- `build_line(record)` — assembles the full `LEVEL source: message` line with optional timestamp prefix. When `record.badges` is non-empty (read with a default, so plain `logging` records still work) `<badges>\t` is inserted between the timestamp and the level, badges joined by single spaces and colored per label (separators uncolored); a line with no badges is byte-identical to before. Does not append `exc_info` or `stack_info`.
- Private helpers `_fmt_asctime`, `_fmt_level`, `_fmt_badges`, `_fmt_source`, `_next_tab_stop`, `_fmt_relative` delegate color application to `self._palette`.

Level display names: `DEBUG`, `ENTER`, `SKIP `, `INFO `, `PASS `, `SUCC.`, `NOTE `, `TIP  `, `DONE `, `HINT `, `IMPT.`, `WARN.`, `CAUT.`, `ERROR`, `FAIL `, `CRIT.`

### `_LogFormatter`

Thin `logging.Formatter` adapter wrapping `_LogFormatEngine`. Accepts a `stream` positional argument forwarded to `AnsiRenderer` for TTY detection. Exposes two public attributes:

- `palette` — the `AnsiRenderer` instance; used directly by `_DiffOnlyEngine` for marker coloring.
- `engine` — the `_LogFormatEngine` instance; used by `_DiffOnlyEngine` for `count_prefix_chars`.

Methods:
- `formatTime(record, datefmt)` — delegates to `engine.format_time`.
- `format(record)` — copies the record, calls `engine.build_line`, then appends `exc_info` and `stack_info` via `Formatter.formatException`/`formatStack`.

### `_TabAlignedLine`

Private `list` subclass representing a line split into `TAB_SIZE`-wide (8)
blocks aligned to tab stops. Used by `_DiffOnlyEngine._compress` to find
leader/full-block/gap boundaries without recomputing tab-stop arithmetic
inline.

- `parse(line, *, start_offset=0)` (classmethod) — expands any literal `\t`
  already present in `line` into spaces (honoring `start_offset` so column
  math stays correct), then splits the expanded line into blocks: the first
  block is shortened by `start_offset` so later blocks land on `TAB_SIZE`
  boundaries, the last block holds the remainder and may be shorter than
  `TAB_SIZE`.
- `render(*, insert_prefix=False, prefix_symbol=" ")` — joins the blocks
  back into a single string; `insert_prefix=True` prepends `start_offset`
  copies of `prefix_symbol`. `__str__` delegates to `render()` with defaults.

### `_DiffOnlyMsgFilter`

Automatically attached to every logger by `getLogger()`. Compresses repeated log lines by replacing characters shared across the last `threshold` (default 3) messages with `〃\t` markers.

`getLogger()` passes a dedicated `_LogFormatter(sys.stdout, …)` as the first positional argument so the filter's palette inherits the same TTY state as the stdout handler. The filter wraps a `_DiffOnlyEngine` which holds all compression state — unless constructed with `disable_diff_only_compression=True`, in which case `_engine` stays `None` and `filter()` returns immediately, leaving each record's message untouched.

Algorithm (`_DiffOnlyEngine`):

1. **Warmup**: the first `threshold` messages pass through unchanged (history fills).
2. **`_common` cache**: `_history` holds each message as a list of lines (split on `\n`). After each message, `_update_common()` recomputes `_common`, one per-position list per line index *k*: the characters common to line *k* of *all* history messages, in O(n × threshold). A line missing from any history message has an empty list, so it never compresses.
3. **Run detection**: on each incoming message, `_compress()` splits it into physical lines and runs `_compress_line()` on each against its own `_common[k]`; only line 1 starts at `count_prefix_chars(record)`, later lines at column 0. The lines are re-joined with `\n`. Within a line, matching positions are marked in O(n).
4. **Word-boundary cut**: for each contiguous common run, `_find_cut()` scans backward from the run end for the nearest word-boundary character, where a *word* character is `0-9A-Za-z` plus `-` and `_` (`_is_word_char`; any other symbol or whitespace is a boundary). The cut lands **on** the boundary character itself, so the symbol prints intact and the changing token keeps its word stem attached (e.g. `/batch_002.csv` — `export` compressed, `/` preserved).
5. **2-tab fallback**: the backward scan reaches back at most `_FALLBACK_TAB_SPAN` (2) tab stops from the run end, measured in rendered columns and floored to a tab-aligned column. When no boundary exists within that span (long unbroken tokens: hashes, URLs), the cut falls back to that tab-aligned floor — a mid-word cut, guaranteeing compression never vanishes on long runs.
6. **Tab-aligned compression**: the replaceable span (`run_s` to `cut`) is split via `_TabAlignedLine.parse(message[run_s:cut], start_offset=prefix_len + run_s)`. A short leading block becomes the *leader* (below), a short trailing block becomes the *gap*, and every full-width block in between compresses into one `_COMPRESSION_MARKER` (`〃\t`) — `〃` (2 wide) + `\t` spans exactly `_TabAlignedLine.TAB_SIZE` (8) visible columns. The gap block (if any) renders as one `_MARKER_CHAR` (`〃`) plus spaces padding exactly to the cut column (spaces only when narrower than `_MARKER_WIDTH`), so every compressed stretch shows a marker and the kept tail always starts at its original rendered column with no leaked common-character fragments. Runs too short for at least one full marker block are printed untouched. Message content that already contains a literal `\t` is expanded to spaces by `_TabAlignedLine.parse` before this split, so embedded tabs never throw off block alignment.
7. **Leader replacement**: the common characters between the run start and the first tab stop (the *leader*, 0-7 columns) are never printed. A leader of `_LEADER_MARKER_MIN` (4) columns or more renders as its own `〃\t` marker; a shorter non-empty leader becomes a bare `\t` jump, letting the tab occupy the space.

8. **Long-line rule**: `_is_long_line(line, prefix_len)` is true when a physical line's rendered, uncompressed width (prefix with badges and tab stops, plus the raw text with embedded tabs expanded) exceeds `_LONG_LINE_COLS` (100). `_render_run()` then swaps tab-aligned dittos for space-separated ones: each full block is `_LONG_LINE_MARKER` (`〃 `), a leader of `_LEADER_MARKER_MIN` or more and a gap of `_MARKER_WIDTH` or more each become one `〃 `, and bare `\t` jumps and gap padding are dropped. Such a line carries no tabs from the compressor and is narrower than its tab form, but it is not guaranteed to fit in 100 columns. The flag is decided per physical line, so one message can mix both forms.

The original (uncompressed) message is stored in `_history` so compression decisions are always based on the raw text, not prior compressed output.

### Comment Banner Utilities

Three public functions that return a fixed-width line by padding `content` with a repeated character to fill `line_width` (default 80). All share the same internal dispatcher `_gen_comment_banner_generic(mode, content, padding, *, line_width, horizontal_offset=0, file, renderer=None)`, which accepts string modes (`"c"`, `"l"`, `"r"`). The `horizontal_offset` kwarg applies only in centered mode; left and right modes ignore it.

The `padding` parameter accepts either a string (single character) or an integer (1-5). Integer shortcuts map to predefined characters: 1→`#`, 2→`=`, 3→`*`, 4→`+`, 5→`-`. The function converts integer padding to its corresponding character before processing.

Each function accepts an optional `renderer` kwarg (`AnsiRenderer or None`). When `None`, a renderer is created from `file` automatically (`file` is otherwise only used for TTY detection). All three functions return the padded line as a `str`; none of them print. When color is enabled, the padding fill is colored grey; `content` and the two-space separators are always uncolored. Callers that invoke the same function repeatedly against the same stream should construct one `AnsiRenderer` up front and pass it via `renderer=` to avoid re-detecting TTY state on every call.

A two-space separator (`_CONTENT_SPACING = "  "`) is always inserted between `content` and the padding fill. For centered mode it is placed on both sides; for left/right modes on one side only.

Input validation (raises `ValueError`):
- `content` must be a single line (no `\n`)
- `len(content)` must not exceed `line_width`
- `padding` (string) must be exactly one printable, non-space character
- `padding` (integer) must be in range 1-5
- `horizontal_offset` (centered mode) must not push either fill side below zero

| function | mode | layout |
| --- | --- | --- |
| `gen_comment_banner_centered` | `"c"` | `grey(padding * left) + "  " + content + "  " + grey(padding * right)` (remainder split evenly; odd char goes right; `left` shifted by `horizontal_offset`) |
| `gen_comment_banner_left_just` | `"l"` | `content + "  " + grey(padding * remaining)` |
| `gen_comment_banner_right_just` | `"r"` | `grey(padding * remaining) + "  " + content` |

### Multi-Line Comment Banner (CB0)

`gen_comment_banner_zero(lines, *, line_width=80, file=sys.stdout, renderer=None)` returns a multi-line boxed banner (CB0) by wrapping each line in an iterable with a grey-colored `# ` prefix, framed by top and bottom grey-colored `#` rulers at full `line_width`.

Input validation (raises `ValueError`):
- Each line must not contain `\n`
- Each line must not exceed `line_width - 2` (reserved for `# ` prefix)

Layout: top ruler + newline-separated prefixed lines + bottom ruler, where `ruler = grey("#" * line_width)` and each line becomes `grey("# ") + line`.

The function returns the formatted banner as a single `str` with embedded newlines; it does not print.

### Command-Line Interface

The module provides a CLI entry point, installed as the `kamilog` console script (see `[project.scripts]` in `pyproject.toml`), with an argparse-based subcommand structure. The `comment_banner` subcommand (alias: `cb`) wraps the comment-banner functions with string-based mode selection.

Both `cb` and `cb0` follow the Unix pipe pattern: text content is read from stdin rather than passed as a positional argument, so each subcommand's remaining positionals are formatting-only (mode, padding, width).

**CLI module organization**:
- `_cli_parser` — root ArgumentParser; only it and `_cli_subparser` are module-level CLI objects, both private under the `_cli_` prefix so they stay off the public surface
- every subcommand is attached by a `_register_*_parser(cli_subparser)` function called on `_cli_subparser` at the bottom of the module; each builds its parser as a local, so no parser object leaks to module scope
- `_common_parser` — `add_help=False` parent `ArgumentParser` holding only a mutually exclusive `-n`/`--newline` and `-N`/`--no-newline` pair (both `dest="newline"`, default `None`); passed via `parents=` to `color` and `color-grey`, and inherited by every other layer below
- `_no_color_parser` — `add_help=False` parent `ArgumentParser`, `parents=[_common_parser]`, adding `-C`/`--no-color`; passed via `parents=` to `logger`, and inherited by `_line_width_parser`
- `_line_width_parser` — `add_help=False` parent `ArgumentParser`, `parents=[_no_color_parser]`, adding `-w`/`--line-width` (default 80); passed via `parents=` to `cb` and `cb0`
- `_calc_line_end(args, stdin_content="")` — resolves `args.newline` and `stdin_content` to the `end` string. Every caller strips stdin's own trailing newline off the content before printing, so `end` is the only place it can survive: it is the *kept* newline (`"\n"` when `stdin_content` ends in one, else `""`) plus the *appended* one. `True` (`-n`) appends one unconditionally, so a stdin ending in a newline yields `"\n\n"`; `False` (`-N`) appends none, yielding just the kept newline; `None` (the default) returns a flat `"\n"`, so auto output always ends in exactly one newline. Used both as the banner/color handlers' `print()` `end` and as the logger's final-record terminator
- `_comment_banner_parser_main(args)` — handler that reads the raw stdin line, derives `content` via `.rstrip("\n")`, maps CLI modes to `_gen_comment_banner_generic`, builds an `AnsiRenderer` honoring `-C`, then prints the returned line to stdout with the newline `_calc_line_end(args, raw)` decides
- `_register_comment_banner_parser(cli_subparser)` — builds and attaches the `comment_banner` / `cb` subcommand, inheriting `_line_width_parser`
- `_COMMENT_BANNER_HELP` — shared help/description string for the subcommand
- `_comment_banner_zero_parser_main(args)` — handler that reads raw stdin, splits it into `lines` (one banner line per stdin line), builds an `AnsiRenderer` honoring `-C`, calls `gen_comment_banner_zero`, then prints the returned banner with the newline `_calc_line_end(args, raw)` decides
- `_register_comment_banner_zero_parser(cli_subparser)` — builds and attaches the `comment_banner_zero` / `cb0` subcommand, inheriting `_line_width_parser`
- `_CB0_HELP` — shared help/description string for the CB0 subcommand
- `_parse_ansi_style(raw)` — argparse `type` adapter wrapping `AnsiStyle.parse`, mapping its `ValueError` to `ArgumentTypeError` so an unknown `STYLE` token reports as a normal argparse usage error
- `_print_colored_stdin_line(args, style)` — shared handler body for `color` and `color-grey`: reads a single stdin line, applies `style` via a plain (non-`-C`-aware) `AnsiRenderer`, and prints with the newline `_calc_line_end(args, raw)` decides
- `_register_color_parser(cli_subparser)` — builds and attaches the `color` / `c` subcommand, inheriting `_common_parser`; `STYLE` is a `nargs="+"` positional of `_parse_ansi_style`-typed tokens, OR-combined into one `AnsiStyle` before rendering
- `_COLOR_HELP` / `_COLOR_DESCRIPTION` — shared help and description strings for the subcommand
- `_register_color_grey_parser(cli_subparser)` — builds and attaches the `color-grey` subcommand, inheriting `_common_parser`; fixed to `AnsiStyle.GREY`, equivalent to `color GREY`
- `_COLOR_GREY_HELP` / `_COLOR_GREY_DESCRIPTION` — shared help and description strings for the subcommand
- `_register_logger_parser(cli_subparser)` — builds and attaches the `logger` / `l` subcommand, inheriting `_no_color_parser`
- `_logger_parser_main(args)` — handler that resolves `LEVEL` and `--time-format` through `_LOGGER_LEVEL_MAP` / `_LOGGER_TIME_FORMAT_MAP`, calls `getLogger(args.name, datefmt=…)`, applies the verbosity threshold, then logs each stdin line at the resolved level. Each record is emitted with the handler's `"\n"` terminator, so the final record's terminator *is* the output's trailing newline: `_calc_line_end(args, raw)` is assigned to every handler's `terminator` immediately before the last line is logged, making `-n` end the output in `"\n\n"`, `-N` keep or omit the break as raw stdin did, and auto end in exactly one. Earlier records are never touched, so internal breaks always survive
- `_LOGGER_HELP` / `_LOGGER_DESCRIPTION` — shared help and description strings for the subcommand

**Comment Banner subcommand (`comment_banner` / `cb`)**:
- Stdin: `CONTENT` — single line of text, read via `sys.stdin.readline()`
- Positional: `MODE` (c/center, l/left, r/right), `PADDING` (char or int 1-5)
- Option: `-w, --line-width LINE_WIDTH` (default 80) — via `_line_width_parser`
- Option: `-n, --newline` / `-N, --no-newline` (force a trailing newline / force none; default auto-detects from whether stdin already ends with a newline) — via `_common_parser`
- Option: `-C, --no-color` (force plain output) — via `_no_color_parser`
- Example: `echo 'hello world' | kamilog cb c '=' -w 20`

**Comment Banner Zero subcommand (`comment_banner_zero` / `cb0`)**:
- Stdin: `LINES` — one or more lines, read via `sys.stdin.read().splitlines()`
- Option: `-w, --line-width LINE_WIDTH` (default 80) — via `_line_width_parser`
- Option: `-n, --newline` / `-N, --no-newline` (force a trailing newline / force none; default auto-detects from whether stdin already ends with a newline) — via `_common_parser`
- Option: `-C, --no-color` (force plain output) — via `_no_color_parser`
- Example: `printf 'Title\nSubtitle\n' | kamilog cb0 -w 40`

**Color subcommand (`color` / `c`)**:
- Stdin: `CONTENT` — single line of text, read via `sys.stdin.readline()`
- Positional: `STYLE` — one or more space-separated `AnsiStyle` member names (`nargs="+"`, each parsed via `_parse_ansi_style`/`AnsiStyle.parse`), OR-combined before rendering
- Option: `-n, --newline` / `-N, --no-newline` (force a trailing newline / force none; default auto-detects from whether stdin already ends with a newline) — via `_common_parser`
- No `-C`/`--no-color` — deliberately not inherited, since disabling color makes no sense for a subcommand whose purpose is applying color
- Example: `echo 'hello world' | kamilog color RED BOLD`

**Color-grey subcommand (`color-grey`)**:
- Stdin: `CONTENT` — single line of text, read via `sys.stdin.readline()`
- No positional — fixed to `AnsiStyle.GREY`, equivalent to `color GREY`
- Option: `-n, --newline` / `-N, --no-newline` — same as `color`, via `_common_parser`
- No `-C`/`--no-color` — same exclusion as `color`
- Example: `echo 'hello world' | kamilog color-grey`

**Logger subcommand (`logger` / `l`)**:
- Stdin: `LINES` — one or more lines, read via `sys.stdin.read().splitlines()`; each is emitted as one log record
- Positional: `LEVEL` — a level name from `_LOGGER_LEVEL_MAP` (`debug`, `enter`, `skip`, `succ`, `info`, `pass`, `note`, `tip`, `done`, `hint`, `important`, `warning`, `caution`, `error`, `fail`, `critical`); `notset` is excluded — `Logger.isEnabledFor(NOTSET)` is always `False`, so a record logged at that level can never actually emit
- Positional: `LOGGER_NAME` — optional, forwarded to `getLogger()` as the `name` argument; defaults to the root logger when omitted
- Option: `--verbosity VERBOSITY` — base verbosity offset the `-v`/`-q` counts adjust from (default 3); the resolved level acts as the print threshold, so records below it are dropped
- Option: `-t, --time-format` — one of `time`, `time-ms`, `datetime`, `datetime-ms`, `no-time` (default `time`), mapped through `_LOGGER_TIME_FORMAT_MAP` to a `datefmt` passed into `getLogger()`; `no-time` maps to `None`
- Option: `-n, --newline` / `-N, --no-newline` — forces / forces off the final stdin line's trailing newline; default auto-detects from whether raw stdin already ends with a newline, via `_common_parser`; earlier records always keep their line breaks
- Option: `-C, --no-color` — force plain output; forwarded to `getLogger(disable_color=True)`, via `_no_color_parser`
- Option: `-D, --no-diff-only` — skip diff-only compression; forwarded to `getLogger(disable_diff_only_compression=True)`
- Option: verbosity flags via `add_verbose_arguments` — `-v`/`-q` (step) plus `-V`/`-Q`/`--max-verbose`/`--max-quiet` (extremity)
- Example: `echo 'disk full' | kamilog logger error`
- Example with a named logger: `echo 'disk full' | kamilog logger error my_module`

## Public API Surface

```python
# logger factory
kamilog.getLogger(name=None, *, datefmt=DATEFMT_TIME, relative_to=None,
                  disable_color=False, disable_diff_only_compression=False,
                  filename=None, file_mode="a", disable_console=False,
                  enable_propagate=False) -> KamiLogger
kamilog.KamiLogger                              # logger class (subclass of logging.Logger)

# ANSI color
kamilog.AnsiStyle                               # combinable Flag enum of style bits
kamilog.AnsiStyle.parse(raw) -> AnsiStyle       # parse comma-separated member names, eg "RED,BOLD"
kamilog.AnsiRenderer(stream=None, *, is_disabled=False)  # TTY-detecting color applier

# comment banner
kamilog.gen_comment_banner_centered(content, padding, *, line_width=80, horizontal_offset=0, file, renderer=None) -> str
kamilog.gen_comment_banner_left_just(content, padding, *, line_width=80, file, renderer=None) -> str
kamilog.gen_comment_banner_right_just(content, padding, *, line_width=80, file, renderer=None) -> str
kamilog.gen_comment_banner_zero(lines, *, line_width=80, file=sys.stdout, renderer=None) -> str

# log level constants
kamilog.NOTSET, DEBUG, ENTER, SKIP, INFO, PASS, SUCC, NOTE, TIP,
DONE, HINT, IMPORTANT, WARNING, CAUTION, ERROR, FAIL, CRITICAL

# timestamp format constants
kamilog.DATEFMT_TIME          # "HH:MM:SS"
kamilog.DATEFMT_TIME_MS       # "HH:MM:SS.mmm"
kamilog.DATEFMT_DATETIME      # "YYYY-MM-DD HH:MM:SS"
kamilog.DATEFMT_DATETIME_MS   # "YYYY-MM-DD HH:MM:SS.mmm"

# verbosity helpers
kamilog.add_verbose_arguments(parser, *, step_flags="vq", extremity_flags="VQ")
kamilog.calc_verbosity(namespace, verbosity=0) -> int
kamilog.calc_logging_level(verbosity, namespace=None) -> int
kamilog.set_logging_level_by_namespace(namespace, verbosity=0, logger=None, logger_name=None)
kamilog.set_logging_level_by_verbosity(verbosity, logger=None, logger_name=None)
```

`calc_verbosity` applies a namespace's `-v`/`-q` counts as an offset to a base
`verbosity` and returns the resulting integer. `calc_logging_level` maps a
verbosity integer to a logging level, and — when passed a `namespace` — folds
in `calc_verbosity`'s offset first. `set_logging_level_by_namespace` and
`set_logging_level_by_verbosity` are thin wrappers composing these two
functions with `logger.setLevel(...)`.

`set_logging_level_by_namespace`'s `verbosity` kwarg sets the base level that
the namespace's `-v`/`-q` counts offset from, instead of always starting at 0.

`add_verbose_arguments` adds two flag families to a parser: **step** flags
(`--verbose`/`--quiet`, `action="count"`) that shift verbosity by ±1 per
occurrence, and **extremity** flags (`--max-verbose`/`--max-quiet`,
`action="store_const"`) that jump straight to ±`_EXTREME_VERBOSITY` (10⁶),
pinning the level to `DEBUG`/`CRITICAL`. All four long options are always
added; the keyword-only `step_flags` and `extremity_flags` (each `"vq"`,
`"VQ"`, or `""`) choose which single-letter short-flag pair — `-v`/`-q`,
`-V`/`-Q`, or none — binds to each family. Raises `ValueError` on an invalid
choice or when both families request the same non-empty pair.

Verbosity mapping (default level is `DONE` = 25):

| flags | verbosity | level |
| --- | --- | --- |
| `-vvv` or more | ≥ 3 | `DEBUG` (10) |
| `-vv` | 2 | `ENTER` (15) |
| `-v` | 1 | `INFO` (20) |
| *(none)* | 0 | `DONE` (25) |
| `-q` | -1 | `WARNING` (30) |
| `-qq` | -2 | `ERROR` (40) |
| `-qqq` or more | ≤ -3 | `CRITICAL` (50) |

## Known Limitations and Future Work

- Test coverage now spans verbosity helpers, comment-banner functions, `AnsiRenderer`/TTY detection (`tests/ansi/`), `_LogFormatter`/`_LogFormatEngine` (`tests/lf/`), badges (`tests/badge/`), `KamiLogger` (`tests/logger/`), `_DiffOnlyEngine`/`_DiffOnlyMsgFilter` (`tests/dof/`), `_TabAlignedLine` (`tests/tal/`), and the shared `-n`/`-N`/`-C` CLI flags (`tests/cli/`), plus golden-output tests for every `examples/` demo script; the CLI subcommands' pre-existing arguments (mode, padding, width, stderr routing, level resolution, verbosity) still have no dedicated tests.
