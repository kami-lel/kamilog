# kamilog Usage Documentation

## Logging

Use `kamilog.getLogger()` in place of `logging.getLogger()` to get a
configured logger instance:

```python
import kamilog

log = kamilog.getLogger("myapp")
log.setLevel(kamilog.DEBUG)

log.debug("Debugging details here")
log.info("Informational message")

try:
    1 / 0
except ZeroDivisionError as err:
    log.exception(err)

log.enter("starting operation")
log.done("operation completed")
log.warning("Warning message")
```

Default output (no timestamp):

```
DEBUG myapp: Debugging details here
INFO  myapp: Informational message
ERROR myapp: division by zero
Traceback (most recent call last):
  File "main.py", line 12, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
ENTER myapp: starting operation
DONE  myapp: operation completed
WARN. myapp: Warning message
```

> [!NOTE]
> Logger name (`myapp:`) is omitted when `name` is `None` or `"root"`.


































## Custom Log Levels

`KamiLogger` adds six levels for hook and test-case workflows. All log levels (native and custom) are shown in the table below, ordered by numeric value:

| Level | Num | Function | Color | ANSI Code | Meaning |
|---|---|---|---|---|---|
| DEBUG | 10 | `.debug()` | Cyan | `\033[36m` | debugging information shown only during development |
| ENTER | 11 | `.enter()` | Bright Cyan | `\033[96m` | marks start of a routine; useful for tracking program logic during development |
| SKIP  | 12 | `.skip()` | Blue | `\033[34m` | marks skipped portion of routine; useful for tracking program logic during development |
| SUCC. | 15 | `.succ()` | Green | `\033[32m` | subroutine or execution succeeded |
| INFO  | 20 | `.info()` | Bright Blue | `\033[94m` | general informational message related to program function |
| PASS  | 21 | `.pass_()` | Bright Green | `\033[92m` | test case passed |
| DONE  | 25 | `.done()` | Bright Yellow | `\033[93m` | entire program or major component completed successfully |
| WARN. | 30 | `.warning()` | Yellow | `\033[33m` | warning condition that should be investigated |
| ERROR | 40 | `.error()` | Red | `\033[31m` | error condition that prevented operation completion |
| FAIL  | 45 | `.fail()` | Bright Red | `\033[91m` | test case or subroutine/execution failed |
| CRIT. | 50 | `.critical()` | Bright Magenta | `\033[95m` | program stopping or crashing immediately |

> [!NOTE]
> `.pass_()` uses a trailing underscore because `pass` is a Python keyword.













### ANSI Color Output

Color is enabled automatically when stdout/stderr is a TTY, and suppressed
when output is piped or redirected to a file.

See the [Custom Log Levels](#custom-log-levels) table for level-to-color mapping (16-color ANSI).

Formatting:
- **Timestamp**: bright black (grey)
- **Level name**: colored (by log level) and bold
- **Source name**: bright black (grey)
- **Colon separator** (`:`) : bright black (grey)
- **Message**: uncolored













### Timestamp Format

By default, no timestamp is shown. Pass `datefmt` to enable it:

| Constant | Value | Example |
|---|---|---|
| (default) | `None` | `INFO  myapp: message` |
| `DATEFMT_TIME` | `"%H:%M:%S"` | `14:30:00 INFO  myapp: message` |
| `DATEFMT_TIME_MS` | `"%H:%M:%S.{ms}"` | `14:30:00.123 INFO  myapp: message` |
| `DATEFMT_DATETIME` | `"%Y-%m-%d %H:%M:%S"` | `2026-06-15 14:30:00 INFO  myapp: message` |
| `DATEFMT_DATETIME_MS` | `"%Y-%m-%d %H:%M:%S.{ms}"` | `2026-06-15 14:30:00.123 INFO  myapp: message` |

```python
# No timestamp (default)
log = kamilog.getLogger("myapp")

# Time only
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_TIME)

# Date and time
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_DATETIME)
```





#### Relative Time

Pass a Unix timestamp as `relative_to` to display elapsed time since that
point instead of wall-clock time. `datefmt` is ignored in this mode.

```python
import time
import kamilog

start = time.time()
log = kamilog.getLogger("myapp", relative_to=start)

log.info("first message")   # +00:00:00.001 [INFO ] myapp:    first message
log.info("later message")   # +00:00:01.234 [INFO ] myapp:    later message
```













### Diff-only Output

`getLogger()` automatically attaches a diff-only filter to every logger. Once three messages have been seen, character positions shared across all of them are compressed: each group of 8 identical characters is replaced by one `〃\t` marker. At least 2 original characters are preserved at each end of the compressed block for visual context.

This means repeated log lines — such as a fixed prefix followed by a changing value — collapse down to show only what changed:

```
INFO  sensor: temperature=21.4 humidity=55% status=OK
INFO  sensor: te〃    ture=21.6 humidity=55% status=OK
INFO  sensor: te〃    ture=21.9 humidity=55% status=OK
```

The filter is invisible during a warmup period (first 3 messages) and resets automatically when the message pattern changes.


































## ANSI Color API

`AnsiColor` and `AnsiRenderer` are public utilities for TTY-aware color application, independent of the logger.

```python
import sys
import kamilog

renderer = kamilog.AnsiRenderer(sys.stdout)

# apply a named color
print(renderer.color("hello", kamilog.AnsiColor.CYAN))

# apply a color with bold
print(renderer.color("hello", kamilog.AnsiColor.GREEN, use_bold=True))

# apply grey (used internally for timestamps and source labels)
print(renderer.color_grey("muted text"))
```

`AnsiRenderer` detects TTY status once at construction. When `stream` is not a TTY (e.g. piped output), all methods return their input unchanged — no escape codes are emitted.

`AnsiColor` members: `GREY`, `CYAN`, `BRIGHT_CYAN`, `BLUE`, `BRIGHT_BLUE`, `GREEN`, `BRIGHT_GREEN`, `YELLOW`, `BRIGHT_YELLOW`, `RED`, `BRIGHT_RED`, `BRIGHT_MAGENTA`, `RESET`, `BOLD`.


## Line Padding

Three functions print a fixed-width line by filling `line_width` (default 80) with a repeated `padding` character around `content`. A two-space separator is always placed between `content` and the fill.

```python
import kamilog

kamilog.print_line_padding_centered("hello", "=")
kamilog.print_line_padding_left_just("hello", "=")
kamilog.print_line_padding_right_just("hello", "=")
```

All three functions accept the same keyword arguments as `print()` (`end`, `file`, `flush`) plus an optional `renderer` kwarg:

```python
import sys
import kamilog

# reuse a renderer across calls for consistent color state
renderer = kamilog.print_line_padding_centered("section", "#")
kamilog.print_line_padding_centered("subsection", "-", renderer=renderer)

# custom width
kamilog.print_line_padding_centered("title", "*", line_width=40)
```

All three raise `ValueError` when:
- `content` contains a newline
- `len(content)` exceeds `line_width`
- `padding` is not exactly one printable non-space character


































## Verbosity and Logging Level

Set up a parser with `-v`/`--verbose` and `-q`/`--quiet` options:

```python
from argparse import ArgumentParser
import kamilog

parser = ArgumentParser()
kamilog.add_verbose_arguments(parser)
```

After parsing, apply the verbosity to a logger:

```python
args = parser.parse_args()

# target the root logger
kamilog.set_logging_level_by_verbosity(args)

# target a named logger by name
kamilog.set_logging_level_by_verbosity(args, logger_name="myapp")

# pass a logger instance directly (takes priority over logger_name)
log = kamilog.getLogger("myapp")
kamilog.set_logging_level_by_verbosity(args, logger=log)
```

Verbosity-to-logging-level mapping:

| Flags | Verbosity | Level | Number |
|---|---|---|---|
| `-vvv` or more | ≥ 3 | `DEBUG` | 10 |
| `-vv` | 2 | `SUCC` | 15 |
| `-v` | 1 | `INFO` | 20 |
| *(none)* | 0 | `DONE` | 25 |
| `-q` | -1 | `WARNING` | 30 |
| `-qq` | -2 | `ERROR` | 40 |
| `-qqq` or more | ≤ -3 | `CRITICAL` | 50 |

