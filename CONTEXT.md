# kamilog CONTEXT

*Last updated: 2026-06-27* (mpl-smart-logging branch)

## Project Overview

kamilog is a lightweight Python logging utility that wraps the stdlib `logging` module. It adds structured output, custom log levels, ANSI 16-color formatting, flexible timestamp options, and a diff-only message filter that compresses repeated log lines. The public API is a single entry point — `kamilog.getLogger()` — that returns a fully configured logger as a drop-in replacement for `logging.getLogger()`.

Repository: <https://github.com/kami-lel/kamilog>

## Repository Layout

```
kamilog/
├── kamilog/
│   ├── __init__.py          # re-exports all public symbols from kamilog.py
│   └── kamilog.py           # entire implementation (~600 lines)
├── tests/
│   ├── verbosity_test.py    # pytest suite for verbosity helpers
│   └── source_quality_test.py  # banned-marker scan (no TODO/FIXME/HACK/BUG)
├── examples/
│   ├── all_levels.py        # all log levels with descriptions
│   ├── basic_logging.py     # standard + custom levels
│   ├── logger_names_and_timestamps.py
│   ├── timestamp_formats.py # all four DATEFMT constants
│   ├── relative_time.py     # elapsed time with relative_to
│   ├── diff_only_filter.py  # _DiffOnlyMsgFilter demo (sensor, batch, sync scenarios)
│   └── verbosity.py         # CLI -v/-q/-qq/-qqq flags
├── docs/
│   ├── usage_doc.md         # public API reference with examples
│   └── install_guide.md     # installation methods
├── setup.cfg                # package metadata; reads version + author via attr:
├── setup.py                 # minimal setuptools stub
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
| `ENTER` | 11 | `"ENTER"` | `"ENTER"` |
| `SKIP` | 12 | `"SKIP"` | `"SKIP "` |
| `SUCC` | 15 | `"SUCC"` | `"SUCC."` |
| `PASS` | 21 | `"PASS"` | `"PASS "` |
| `DONE` | 25 | `"DONE"` | `"DONE "` |
| `FAIL` | 45 | `"FAIL"` | `"FAIL "` |

Module-level aliases (`ENTER = _CustomLogLevel.ENTER`, etc.) keep the public API unchanged. `_PADDED_LEVELNAME_MAP`, `_ANSI_LEVEL_COLORS`, and `KamiLogger`'s log methods all reference `_CustomLogLevel` directly.

### `getLogger(name, *, datefmt, relative_to)`

The sole public entry point. Every call:

1. Retrieves or creates a stdlib logger and upgrades it to `KamiLogger` via `__class__` assignment.
2. Attaches a `_DiffOnlyMsgFilter` instance if one is not already present.
3. Adds stdout and stderr `StreamHandler`s (with `_LogFormatter`) if no handlers exist yet — stdout for `< WARNING`, stderr for `>= WARNING`.

### `KamiLogger`

Subclasses `logging.Logger`. Adds six convenience methods mapping to the custom levels:

| method | level name | numeric |
| --- | --- | --- |
| `.enter()` | `ENTER` | 11 |
| `.skip()` | `SKIP` | 12 |
| `.succ()` | `SUCC` | 15 |
| `.pass_()` | `PASS` | 21 |
| `.done()` | `DONE` | 25 |
| `.fail()` | `FAIL` | 45 |

The full level progression: `DEBUG`(10) → `ENTER`(11) → `SKIP`(12) → `SUCC`(15) → `INFO`(20) → `PASS`(21) → `DONE`(25) → `WARNING`(30) → `ERROR`(40) → `FAIL`(45) → `CRITICAL`(50).

### `_LogFormatter`

Produces `LEVEL  source: message` lines (5-char padded level name, space-separated). Behavior:

- **Color**: per-level ANSI 16-color; auto-disabled when stdout/stderr is not a TTY. Scheme: `DEBUG`/`ENTER` cyan/bright cyan; `SKIP`/`INFO` blue/bright blue; `SUCC` green; `PASS` bright green; `DONE` bright yellow; `WARN.` yellow; `ERROR` red; `FAIL` bright red; `CRIT.` bright magenta.
- **Timestamps**: disabled by default. Enable via `datefmt` (strftime format string using `DATEFMT_*` constants) or `relative_to` (Unix timestamp; displays signed elapsed seconds).
- **Record isolation**: copies the log record before formatting to prevent mutation across handlers.

Level display names: `DEBUG`, `ENTER`, `SKIP.`, `INFO `, `PASS.`, `SUCC.`, `DONE.`, `WARN.`, `ERROR`, `FAIL.`, `CRIT.`

### `_DiffOnlyMsgFilter`

Automatically attached to every logger by `getLogger()`. Compresses repeated log lines by replacing characters shared across the last `window` (default 3) messages with `〃\t` markers.

Algorithm:

1. **Warmup**: the first `window` messages pass through unchanged (history fills).
2. **`_common` cache**: after each message, `_update_common()` recomputes a per-position list of characters common to *all* history messages in O(n × window).
3. **Run detection**: on each incoming message, `filter()` marks positions where the message matches `_common` in O(n).
4. **Tab compression**: contiguous common runs compress in multiples of 8: each 8-char block → one `〃\t` pair. Constraints:
   - at least 2 original chars are preserved before the first marker (or from the run start if the run begins at position ≥ 2 in the message)
   - at least 2 original chars are preserved after the last marker
   - runs shorter than 10 chars are never compressed

The original (uncompressed) message is stored in `_history` so compression decisions are always based on the raw text, not a prior compressed output.

## Public API Surface

```python
kamilog.getLogger(name=None, *, datefmt=None, relative_to=None) -> KamiLogger

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
- Test coverage is limited to verbosity helpers and a banned-marker scan; no unit tests for `_LogFormatter` or `_DiffOnlyMsgFilter`.
