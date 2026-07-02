# kamilog CONTEXT

*Last updated: 2026-07-02 (v2.2.0)*

## Project Overview

kamilog is a lightweight Python logging utility that wraps the stdlib `logging` module. It adds structured output, custom log levels, ANSI 16-color formatting, flexible timestamp options, and a diff-only message filter that compresses repeated log lines. The public API is a single entry point — `kamilog.getLogger()` — that returns a fully configured logger as a drop-in replacement for `logging.getLogger()`.

Repository: <https://github.com/kami-lel/kamilog>

## Repository Layout

```
kamilog/
├── kamilog/
│   ├── __init__.py          # re-exports all public symbols from kamilog.py
│   └── kamilog.py           # entire implementation (~990 lines)
├── tests/
│   ├── cb/                          # comment-banner test suite
│   │   ├── cb-centered_test.py
│   │   ├── cb-left_just_test.py
│   │   ├── cb-right_just_test.py
│   │   └── cb-validation_test.py
│   ├── v/                           # verbosity helper test suite
│   │   ├── v-add_verbose_arguments_test.py
│   │   ├── v-calc_logging_level_test.py
│   │   ├── v-calc_logging_level_namespace_test.py
│   │   └── v-set_logging_level_by_verbosity_test.py
│   └── source_quality_test.py       # banned-marker scan (no TODO/FIXME/HACK/BUG)
├── examples/
│   ├── cb/
│   │   ├── cb-demo.py                       # all three comment-banner functions with char padding
│   │   ├── cb-number-demo.py                # numeric padding shortcuts (1-5)
│   │   └── cb-zero_demo.py                  # multi-line boxed banner (CB0)
│   ├── verbosity_demo.py                    # CLI -v/-q flags with custom levels
│   └── logger/
│       ├── logger-all_levels_demo.py        # all eleven log levels with descriptions
│       ├── logger-timestamps_demo.py        # all four DATEFMT_* formats and relative_to
│       ├── logger-diff_only_demo.py         # _DiffOnlyMsgFilter compression walkthrough
│       └── logger-diff_only_stress_demo.py  # short vs. long message compression contrast
├── docs/
│   ├── usage_doc.md         # public API reference with examples
│   └── install_guide.md     # installation methods
├── pyproject.toml           # PEP 518 build config; package metadata with dynamic version/author
├── requirements.txt         # pytest (test-only)
├── CHANGELOG.md
└── README.md
```

## Architecture

The entire library lives in `kamilog/kamilog.py`. There is no build step and no external runtime dependency.

### `_CustomLogLevel`

Private `IntEnum` subclass that consolidates every custom log level in one place. Each member stores two values: the numeric level (the enum's int value, used wherever an int is expected) and a 5-char padded display name accessed via `.display`. The `.name` property yields the bare name string used in `logging.addLevelName()`.

| member | value | `.name` | `.display` |
| --- | --- | --- | --- |
| `SUCC` | 15 | `"SUCC"` | `"SUCC."` |
| `ENTER` | 16 | `"ENTER"` | `"ENTER"` |
| `SKIP` | 17 | `"SKIP"` | `"SKIP "` |
| `PASS` | 21 | `"PASS"` | `"PASS "` |
| `DONE` | 25 | `"DONE"` | `"DONE "` |
| `FAIL` | 45 | `"FAIL"` | `"FAIL "` |

Module-level aliases (`ENTER = _CustomLogLevel.ENTER`, etc.) keep the public API unchanged. `_PADDED_LEVELNAME_MAP` and `KamiLogger`'s log methods all reference `_CustomLogLevel` directly.

### `AnsiColor`

Public `Enum` of ANSI escape code constants keyed by descriptive color names. Each member's `.value` is the escape sequence string.

| member | escape sequence | usage |
| --- | --- | --- |
| `RESET` | `\033[0m` | terminator for all color codes |
| `BOLD` | `\033[1m` | intensity modifier (applies to foreground) |
| `GREY` | `\033[90m` | bright black; used for timestamps, source labels, markers |
| `CYAN`, `BRIGHT_CYAN` | `\033[36m`, `\033[96m` | `DEBUG`, `ENTER` levels |
| `BLUE`, `BRIGHT_BLUE` | `\033[34m`, `\033[94m` | `SKIP`, `INFO` levels |
| `GREEN`, `BRIGHT_GREEN` | `\033[32m`, `\033[92m` | `SUCC`, `PASS` levels |
| `YELLOW`, `BRIGHT_YELLOW` | `\033[33m`, `\033[93m` | `WARNING`, `DONE` levels |
| `RED`, `BRIGHT_RED` | `\033[31m`, `\033[91m` | `ERROR`, `FAIL` levels |
| `BRIGHT_MAGENTA` | `\033[95m` | `CRITICAL` level |

### `AnsiRenderer`

Public class that centralizes ANSI color detection and application. Instantiated by `_LogFormatter` and exposed via its `palette` attribute; also reachable from `_DiffOnlyEngine` as `formatter.palette`.

- Detects TTY status once at construction via `stream.isatty()`; when `stream` is `None` or not a TTY, all methods return their input unchanged.
- `color(text, color, *, use_bold=False)` — generic color applier; wraps `text` in the given `AnsiColor` code, optionally with bold.
- `color_level(text, levelno)` — wraps `text` in bold + per-level ANSI color codes via the internal `_LEVEL_COLORS` map.
- `color_grey(text)` — wraps `text` in grey codes; used for timestamps, source labels, and compression markers.

### `getLogger(name, *, datefmt, relative_to)`

The sole public entry point. Every call:

1. Retrieves or creates a stdlib logger and upgrades it to `KamiLogger` via `__class__` assignment.
2. Attaches a `_DiffOnlyMsgFilter` instance if one is not already present.
3. Adds stdout and stderr `StreamHandler`s (with `_LogFormatter`) if no handlers exist yet — stdout for `< WARNING`, stderr for `>= WARNING`.

### `KamiLogger`

Subclasses `logging.Logger`. Adds six convenience methods mapping to the custom levels:

| method | level name | numeric |
| --- | --- | --- |
| `.succ()` | `SUCC` | 15 |
| `.enter()` | `ENTER` | 16 |
| `.skip()` | `SKIP` | 17 |
| `.pass_()` | `PASS` | 21 |
| `.done()` | `DONE` | 25 |
| `.fail()` | `FAIL` | 45 |

The full level progression: `DEBUG`(10) → `SUCC`(15) → `ENTER`(16) → `SKIP`(17) → `INFO`(20) → `PASS`(21) → `DONE`(25) → `WARNING`(30) → `ERROR`(40) → `FAIL`(45) → `CRITICAL`(50).

### `_LogFormatEngine`

Holds all core formatting logic, independent of `logging.Formatter`. Instantiated by `_LogFormatter` and exposed via its `engine` attribute. Takes an `AnsiRenderer` instance at construction; all color output is routed through the palette.

Responsibilities:

- `count_prefix_chars(record)` — returns the printable character count before the message text for a given record. Accounts for the optional timestamp (relative: always 13 chars; datefmt: rendered `time.strftime` length), the 5-char padded level name, and the source name with colon. ANSI escape codes are excluded. Uses `time.strftime` directly so there is no dependency on `Formatter`.
- `format_time(record, datefmt)` — produces the optionally colored timestamp string, or an empty string when disabled.
- `build_line(record)` — assembles the full `LEVEL source: message` line with optional timestamp prefix. Does not append `exc_info` or `stack_info`.
- Private helpers `_fmt_asctime`, `_fmt_level`, `_fmt_source`, `_fmt_relative` delegate color application to `self._palette`.

Level display names: `DEBUG`, `ENTER`, `SKIP `, `INFO `, `PASS `, `SUCC.`, `DONE `, `WARN.`, `ERROR`, `FAIL `, `CRIT.`

### `_LogFormatter`

Thin `logging.Formatter` adapter wrapping `_LogFormatEngine`. Accepts a `stream` positional argument forwarded to `AnsiRenderer` for TTY detection. Exposes two public attributes:

- `palette` — the `AnsiRenderer` instance; used directly by `_DiffOnlyEngine` for marker coloring.
- `engine` — the `_LogFormatEngine` instance; used by `_DiffOnlyEngine` for `count_prefix_chars`.

Methods:
- `formatTime(record, datefmt)` — delegates to `engine.format_time`.
- `format(record)` — copies the record, calls `engine.build_line`, then appends `exc_info` and `stack_info` via `Formatter.formatException`/`formatStack`.

### `_DiffOnlyMsgFilter`

Automatically attached to every logger by `getLogger()`. Compresses repeated log lines by replacing characters shared across the last `window` (default 3) messages with `〃\t` markers.

`getLogger()` passes a dedicated `_LogFormatter(sys.stdout, …)` as the first positional argument so the filter's palette inherits the same TTY state as the stdout handler. The filter wraps a `_DiffOnlyEngine` which holds all compression state.

Algorithm (`_DiffOnlyEngine`):

1. **Warmup**: the first `window` messages pass through unchanged (history fills).
2. **`_common` cache**: after each message, `_update_common()` recomputes a per-position list of characters common to *all* history messages in O(n × window).
3. **Run detection**: on each incoming message, `_compress()` marks positions where the message matches `_common` in O(n).
4. **Tab-aligned compression**: contiguous common runs compress in multiples of `_COMPRESSION_BLOCK_SIZE` (8). Each `_COMPRESSION_MARKER` (`〃\t`) is placed at the next column that is a multiple of 8 measured from the rendered line start (`formatter.engine.count_prefix_chars` + message offset), so `〃` (2 wide) + `\t` spans exactly 8 visible columns. At least `_PRESERVED_TRAILING_CHARS` (2) original chars are kept at the trailing end of each run.

The original (uncompressed) message is stored in `_history` so compression decisions are always based on the raw text, not prior compressed output.

### Comment Banner Utilities

Three public functions that return a fixed-width line by padding `content` with a repeated character to fill `line_width` (default 80). All share the same internal dispatcher `_gen_comment_banner_generic(mode, content, padding, *, line_width, file, renderer=None)`, which accepts string modes (`"c"`, `"l"`, `"r"`).

The `padding` parameter accepts either a string (single character) or an integer (1-5). Integer shortcuts map to predefined characters: 1→`#`, 2→`=`, 3→`*`, 4→`+`, 5→`-`. The function converts integer padding to its corresponding character before processing.

Each function accepts an optional `renderer` kwarg (`AnsiRenderer or None`). When `None`, a renderer is created from `file` automatically (`file` is otherwise only used for TTY detection). All three functions return the padded line as a `str`; none of them print. When color is enabled, the padding fill is colored grey; `content` and the two-space separators are always uncolored. Callers that invoke the same function repeatedly against the same stream should construct one `AnsiRenderer` up front and pass it via `renderer=` to avoid re-detecting TTY state on every call.

A two-space separator (`_CONTENT_SPACING = "  "`) is always inserted between `content` and the padding fill. For centered mode it is placed on both sides; for left/right modes on one side only.

Input validation (raises `ValueError`):
- `content` must be a single line (no `\n`)
- `len(content)` must not exceed `line_width`
- `padding` (string) must be exactly one printable, non-space character
- `padding` (integer) must be in range 1-5

| function | mode | layout |
| --- | --- | --- |
| `gen_comment_banner_centered` | `"c"` | `grey(padding * left) + "  " + content + "  " + grey(padding * right)` (remainder split evenly; odd char goes right) |
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

The module provides a CLI entry point via direct script execution (`python kamilog/kamilog.py`) with an argparse-based subcommand structure. The `comment_banner` subcommand (alias: `cb`) wraps the comment-banner functions with string-based mode selection.

Note: `python -m kamilog` does not work — the package has no `kamilog/__main__.py`. Use direct script execution (`python kamilog/kamilog.py`) instead.

Both `cb` and `cb0` follow the Unix pipe pattern: text content is read from stdin rather than passed as a positional argument, so each subcommand's remaining positionals are formatting-only (mode, padding, width).

**CLI module organization**:
- `cli_parser` — root ArgumentParser with `cli_subparser` for subcommands
- `_comment_banner_parser_main(args)` — handler that reads `content` from stdin (single line), maps CLI modes to `_gen_comment_banner_generic`, then prints the returned line to stdout or stderr
- `_COMMENT_BANNER_HELP` — shared help/description string for the subcommand
- `_comment_banner_zero_parser_main(args)` — handler that reads `lines` from stdin (one banner line per stdin line), calls `gen_comment_banner_zero`, then prints the returned banner
- `_CB0_HELP` — shared help/description string for the CB0 subcommand

**Comment Banner subcommand (`comment_banner` / `cb`)**:
- Stdin: `CONTENT` — single line of text, read via `sys.stdin.readline()`
- Positional: `MODE` (c/center, l/left, r/right), `PADDING` (char or int 1-5)
- Option: `-w, --line-width LINE_WIDTH` (default 80)
- Option: `-e, --stderr` (output to stderr)
- Example: `echo 'hello world' | python kamilog/kamilog.py cb c '=' -w 20`

**Comment Banner Zero subcommand (`comment_banner_zero` / `cb0`)**:
- Stdin: `LINES` — one or more lines, read via `sys.stdin.read().splitlines()`
- Option: `-w, --line-width LINE_WIDTH` (default 80)
- Option: `-e, --stderr` (output to stderr)
- Example: `printf 'Title\nSubtitle\n' | python kamilog/kamilog.py cb0 -w 40`

## Public API Surface

```python
# logger factory
kamilog.getLogger(name=None, *, datefmt=None, relative_to=None) -> KamiLogger
kamilog.KamiLogger                              # logger class (subclass of logging.Logger)

# ANSI color
kamilog.AnsiColor                               # Enum of ANSI escape codes
kamilog.AnsiRenderer                            # TTY-detecting color applier

# comment banner
kamilog.gen_comment_banner_centered(content, padding, *, line_width=80, file, renderer=None) -> str
kamilog.gen_comment_banner_left_just(content, padding, *, line_width=80, file, renderer=None) -> str
kamilog.gen_comment_banner_right_just(content, padding, *, line_width=80, file, renderer=None) -> str
kamilog.gen_comment_banner_zero(lines, *, line_width=80, file=sys.stdout, renderer=None) -> str

# log level constants
kamilog.NOTSET, DEBUG, ENTER, SKIP, INFO, PASS, SUCC, DONE,
WARNING, ERROR, FAIL, CRITICAL

# timestamp format constants
kamilog.DATEFMT_TIME          # "HH:MM:SS"
kamilog.DATEFMT_TIME_MS       # "HH:MM:SS.mmm"
kamilog.DATEFMT_DATETIME      # "YYYY-MM-DD HH:MM:SS"
kamilog.DATEFMT_DATETIME_MS   # "YYYY-MM-DD HH:MM:SS.mmm"

# verbosity helpers
kamilog.add_verbose_arguments(parser)
kamilog.set_logging_level_by_verbosity(namespace, logger=None, logger_name=None)
```

Verbosity mapping (default level is `DONE` = 25):

| flags | verbosity | level |
| --- | --- | --- |
| `-vvv` or more | ≥ 3 | `DEBUG` (10) |
| `-vv` | 2 | `SUCC` (15) |
| `-v` | 1 | `INFO` (20) |
| *(none)* | 0 | `DONE` (25) |
| `-q` | -1 | `WARNING` (30) |
| `-qq` | -2 | `ERROR` (40) |
| `-qqq` or more | ≤ -3 | `CRITICAL` (50) |

## Known Limitations and Future Work

- No file handler option on `getLogger()` — stdout/stderr only.
- Test coverage spans verbosity helpers and comment-banner functions; no unit tests for `_LogFormatter` or `_DiffOnlyMsgFilter`.
