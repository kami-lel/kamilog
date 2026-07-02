# kamilog Usage Documentation

## Custom Logging

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


































### Custom Log Levels

`KamiLogger` extends the standard library logger with six custom levels for test and hook workflows. Full level reference:

| Level | Num | Function | Color | ANSI Code | Meaning |
|---|---|---|---|---|---|
| DEBUG | 10 | `.debug()` | Cyan | `\033[36m` | internal program state and control flow |
| ENTER | 11 | `.enter()` | Bright Cyan | `\033[96m` | starting a subroutine or code section |
| SKIP  | 12 | `.skip()` | Blue | `\033[34m` | code section was skipped |
| SUCC. | 15 | `.succ()` | Green | `\033[32m` | operation succeeded |
| INFO  | 20 | `.info()` | Bright Blue | `\033[94m` | general program event or state change |
| PASS  | 21 | `.pass_()` | Bright Green | `\033[92m` | test assertion or case passed |
| DONE  | 25 | `.done()` | Bright Yellow | `\033[93m` | program or major phase completed successfully |
| WARN. | 30 | `.warning()` | Yellow | `\033[33m` | unexpected but recoverable condition |
| ERROR | 40 | `.error()` | Red | `\033[31m` | operation failed |
| FAIL  | 45 | `.fail()` | Bright Red | `\033[91m` | test assertion or case failed |
| CRIT. | 50 | `.critical()` | Bright Magenta | `\033[95m` | program failure or immediate crash |

> [!IMPORTANT]
> `.pass_()` uses a trailing underscore because `pass` is a Python keyword.

> [!TIP]
> **DEBUG vs INFO**: Use `DEBUG` to trace internal program state and control flow during development. Use `INFO` for general events and state changes that occur in normal execution.

> [!TIP]
> **WARN., ERROR, CRIT. for error escalation**: Use `WARN.` for unexpected but recoverable conditions. Use `ERROR` when operations fail but recovery is possible. Use `CRIT.` when the program must terminate.

> [!TIP]
> **ENTER, SKIP, SUCC. for subroutines**: Track major code sections with `ENTER` at the start. Pair with `SUCC.` upon completion. Use `SKIP` when sections are conditionally skipped.

> [!TIP]
> **DONE for program completion**: Use `DONE` only once at the end to indicate the entire program or major phase completed successfully.

> [!TIP]
> **PASS and FAIL for testing**: Use `PASS` and `FAIL` exclusively in test scripts. Each test case branch should log either `.pass_()` or `.fail()` depending on the outcome.













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


































## ANSI Colored Output

`AnsiColor` and `AnsiRenderer` provide TTY-aware color application independent of logging.

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






































































































































## Comment Banner

Three functions return fixed-width lines padded with a fill character: `gen_comment_banner_centered`, `gen_comment_banner_left_just`, `gen_comment_banner_right_just`. A two-space separator is always placed between content and fill. Print the result yourself:

```python
import kamilog

print(kamilog.gen_comment_banner_centered("hello", "="))
print(kamilog.gen_comment_banner_left_just("hello", "="))
print(kamilog.gen_comment_banner_right_just("hello", "="))
```

### Padding

The `padding` parameter accepts either a string (single character) or an integer (1-5):

| padding | character |
|---|---|
| `"#"` or `1` | `#` |
| `"="` or `2` | `=` |
| `"*"` or `3` | `*` |
| `"+"` or `4` | `+` |
| `"-"` or `5` | `-` |

```python
# String padding
print(kamilog.gen_comment_banner_centered("release", "="))

# Integer padding (shorter to type)
print(kamilog.gen_comment_banner_centered("release", 2))
```

### Renderer Reuse

All three functions accept `line_width` (default `80`), `file` (used only for ANSI TTY detection; defaults to `sys.stdout`), and an optional `renderer` kwarg. If you call any of them repeatedly, construct one `AnsiRenderer` up front and pass it in — this avoids re-detecting TTY state on every call:

```python
renderer = kamilog.AnsiRenderer(sys.stdout)
print(kamilog.gen_comment_banner_centered("section", 1, renderer=renderer))
print(kamilog.gen_comment_banner_centered("subsection", 5, renderer=renderer))

# custom width
print(kamilog.gen_comment_banner_centered("title", 3, line_width=40))
```

### Validation

All three raise `ValueError` when:
- `content` contains a newline
- `len(content)` exceeds `line_width`
- `padding` (string) is not exactly one printable non-space character
- `padding` (int) is not in range 1-5




































## Verbosity and Logging Level

Map CLI flags (`-v`/`--verbose`, `-q`/`--quiet`) to logging levels with built-in helpers:

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


































## Command-Line Interface

The comment-banner utilities are accessible via CLI:

```bash
python kamilog/kamilog.py comment_banner -h
```
