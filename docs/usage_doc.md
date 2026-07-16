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

`KamiLogger` extends the standard library logger with ten custom levels for test and hook workflows. Full level reference:

| Level | Num | Function | Color | Remark |
|---|---|---|---|---|
| DEBUG | 10 | `.debug()` | `CYAN` | internal state and control flow, kept to Debug output and never shown to users |
| ENTER | 15 | `.enter()` | `BRIGHT_CYAN` | enters a subroutine or test section, a Developer trace of flow |
| SKIP  | 16 | `.skip()` | `BLUE` | a logic branch or test case was Expectedly skipped |
| SUCC. | 17 | `.succ()` | `GREEN` | a subroutine completed successfully, Pairs with ENTER |
| INFO  | 20 | `.info()` | `BRIGHT_BLUE` | a general event or state Change during normal execution |
| PASS  | 21 | `.pass_()` | `BRIGHT_GREEN` | a test assertion or case Passed |
| NOTE  | 23 | `.note()` | `BLUE` | an aside worth Recording for the production user |
| TIP   | 24 | `.tip()` | `BRIGHT_CYAN` | an actionable Suggestion for the production user |
| DONE  | 25 | `.done()` | `BRIGHT_YELLOW` | an entire program or major Phase finished successfully |
| HINT  | 26 | `.hint()` | `CYAN` | a subtle actionable cue Printed to the terminal |
| IMPT. | 27 | `.important()` | `BRIGHT_BLUE` | emphasized terminal information that should Stand Out |
| WARN. | 30 | `.warning()` | `YELLOW` | an unexpected but Recoverable condition |
| CAUT. | 31 | `.caution()` | `MAGENTA` | needs even more Immediate attention than IMPT |
| ERROR | 40 | `.error()` | `RED` | an operation Failed |
| FAIL  | 45 | `.fail()` | `BRIGHT_RED` | a test assertion or case Failed |
| CRIT. | 50 | `.critical()` | `BRIGHT_MAGENTA` | program failure or immediate Crash |

> [!IMPORTANT]
> `.pass_()` uses a trailing underscore because `pass` is a Python keyword.

**Development logging: `DEBUG`, `ENTER`, `SKIP`, `SUCC.`.** These levels help a developer follow the structure and flow of ordinary execution, and none of them are meant for a production user. `DEBUG` traces internal state and control flow. `ENTER` marks the start of a major subroutine or section; pair it at the top with `SUCC.` on successful completion. `SKIP` marks the expected skip of a logic branch that was deliberately not taken.

**Test conditions: `ENTER`, `SKIP`, `PASS`, `FAIL`.** These track the flow of a test script and are likewise developer-facing, not for a production user. `ENTER` marks the start of a major test section. Each test-case branch then logs exactly one of `PASS` or `FAIL` — a passing assertion or a failing one. `SKIP` marks a test case that is deliberately not run.

**Production logging: `INFO`, `NOTE`, `TIP`, `DONE`.** These are addressed to the production user and can be expected to land in the production logs. `INFO` records a general event or state change during normal execution, while `NOTE` is a plainer aside worth keeping and `TIP` offers an actionable suggestion. `DONE` fires once, at the successful finish of an entire program or major phase — it is the production-facing counterpart to the developer-only `SUCC.`.

**Terminal attention: `HINT`, `IMPT.`, `CAUT.`.** These are expected to be printed to the terminal, so they usually point at something the user should actually do. `HINT` is the quietest of the three. `IMPT.` is emphasized information that should stand out. `CAUT.` escalates one step further, demanding even more immediate attention than `IMPT.`.

**Error escalation: `WARN.`, `ERROR`, `CRIT.`.** These form a ladder of increasing severity — a recoverable surprise, a failed operation, and an outright crash — logged in that order as a situation worsens.












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

Pass `disable_color=True` to force plain output on every handler and the
diff-only filter, regardless of TTY state:

```python
log = kamilog.getLogger("myapp", disable_color=True)
```













### Timestamp Format

By default, timestamps are shown as `HH:MM:SS` (`DATEFMT_TIME`). Pass a
different `datefmt` constant to change the format, or `None` to disable
timestamps:

| Constant | Value | Example |
|---|---|---|
| `DATEFMT_TIME` (default) | `"%H:%M:%S"` | `14:30:00 INFO  myapp: message` |
| `DATEFMT_TIME_MS` | `"%H:%M:%S.{ms}"` | `14:30:00.123 INFO  myapp: message` |
| `DATEFMT_DATETIME` | `"%Y-%m-%d %H:%M:%S"` | `2026-06-15 14:30:00 INFO  myapp: message` |
| `DATEFMT_DATETIME_MS` | `"%Y-%m-%d %H:%M:%S.{ms}"` | `2026-06-15 14:30:00.123 INFO  myapp: message` |
| (disabled) | `None` | `INFO  myapp: message` |

```python
# Time only (default)
log = kamilog.getLogger("myapp")

# Date and time
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_DATETIME)

# No timestamp
log = kamilog.getLogger("myapp", datefmt=None)
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

`getLogger()` automatically attaches a diff-only filter to every logger. Once three messages have been seen, character positions shared across all of them are compressed: each group of 8 identical characters is replaced by one `〃\t` marker. Each compressed stretch ends at a word boundary (`0-9A-Za-z`, `-`, and `_` count as word characters), so a changing token keeps its full word intact; long unbroken tokens such as hashes or URLs fall back to a tab-aligned mid-word cut so compression never vanishes.

This means repeated log lines — such as a fixed prefix followed by a changing value — collapse down to show only what changed:

```
INFO  sensor: temperature=21.4 humidity=55% status=OK
INFO  sensor: te〃    ture=21.6 humidity=55% status=OK
INFO  sensor: te〃    ture=21.9 humidity=55% status=OK
```

The filter is invisible during a warmup period (first 3 messages) and resets automatically when the message pattern changes.

Pass `disable_diff_only_compression=True` to turn compression off entirely, so
every record prints in full:

```python
log = kamilog.getLogger("myapp", disable_diff_only_compression=True)
```













### File Output

Pass `filename` to `getLogger()` to also write the kamilog format to a log
file. Color is always disabled for the file, and every level lands in the
one file (no stdout/stderr split):

```python
import kamilog

# log to console *and* app.log
log = kamilog.getLogger("myapp", filename="app.log")
```

Related options:

- `disable_console=True` — skip the stdout/stderr handlers for a **file-only** logger
- `file_mode` — open mode forwarded to `logging.FileHandler`; default `"a"` (append), pass `"w"` to truncate

The file handler is attached idempotently per resolved path, so repeated
`getLogger()` calls with the same `name` and `filename` never stack
duplicate handlers.


































## ANSI Colored Output

`AnsiStyle` and `AnsiRenderer` provide TTY-aware color application independent of logging.

```python
import sys
import kamilog

renderer = kamilog.AnsiRenderer(sys.stdout)
S = kamilog.AnsiStyle

# apply a named color
print(renderer.color("hello", S.CYAN))

# combine flags with `|` — foreground, background, bold, underline
print(renderer.color("hello", S.BOLD | S.GREEN | S.BG_BLUE))

# apply grey (used internally for timestamps and source labels)
print(renderer.color_grey("muted text"))

# color a triage tag, hue picked by tag type (BUG/FIXME/TODO/HACK)
print(renderer.color_triage_tag("TODO"))
```

`AnsiRenderer` detects TTY status once at construction. When `stream` is not a TTY (e.g. piped output), all methods return their input unchanged — no escape codes are emitted.

`AnsiStyle` is a combinable `Flag` enum. Foreground members: `RED`, `BRIGHT_RED`, `YELLOW`, `BRIGHT_YELLOW`, `GREEN`, `BRIGHT_GREEN`, `CYAN`, `BRIGHT_CYAN`, `BLUE`, `BRIGHT_BLUE`, `MAGENTA`, `BRIGHT_MAGENTA`, `BLACK`, `GREY`, `WHITE`, `BRIGHT_WHITE`. Each has a `BG_`-prefixed background counterpart (e.g. `BG_RED`, `BG_BRIGHT_CYAN`). Style members: `BOLD`, `UNDERLINE`.

`color_triage_tag(triage_tag)` colors any of the 12 triage-tag strings — `BUG`/`Bug`/`bug`, `FIXME`/`Fixme`/`fixme`, `TODO`/`Todo`/`todo`, `HACK`/`Hack`/`hack` — using one hue per tag type, with contrast escalating for louder (more-capitalized) tiers. Raises `ValueError` for any other string.


































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

### Horizontal Offset

`gen_comment_banner_centered` accepts `horizontal_offset` (default `0`) to nudge the centered content sideways — negative shifts it left, positive shifts it right. This keeps a centered title aligned when the banner is printed after a left-hand prefix: shrink `line_width` by the prefix width and offset by half of it.

```python
# bare centered banner across the full width
print(kamilog.gen_comment_banner_centered("results", "="))

# 8-char prefix; width drops by 8, offset -4 realigns the title
print("phase 2 " + kamilog.gen_comment_banner_centered(
    "results", "=", line_width=72, horizontal_offset=-4
))
```

The offset applies only to centered banners; the left- and right-justified functions ignore it.

### Validation

All three raise `ValueError` when:
- `content` contains a newline
- `len(content)` exceeds `line_width`
- `padding` (string) is not exactly one printable non-space character
- `padding` (int) is not in range 1-5

`gen_comment_banner_centered` additionally raises when `horizontal_offset` pushes either fill side below zero.




































## Verbosity and Logging Level

Built-in helpers map verbosity, from either CLI flags or a plain integer, to
logging levels.













### CLI Flags

Add `-v`/`--verbose` and `-q`/`--quiet` to a parser:

```python
from argparse import ArgumentParser
import kamilog

parser = ArgumentParser()
kamilog.add_verbose_arguments(parser)
```

After parsing, apply the verbosity to a logger with
`set_logging_level_by_namespace`:

```python
args = parser.parse_args()

# target the root logger
kamilog.set_logging_level_by_namespace(args)

# target a named logger by name
kamilog.set_logging_level_by_namespace(args, logger_name="myapp")

# pass a logger instance directly (takes priority over logger_name)
log = kamilog.getLogger("myapp")
kamilog.set_logging_level_by_namespace(args, logger=log)
```

Pass `verbosity` to shift the base level that `-v`/`-q` counts are added
to/subtracted from, instead of starting from `0`:

```python
# start two steps quieter, then apply -v/-q on top
kamilog.set_logging_level_by_namespace(args, verbosity=-2)
```













### Verbosity Integer

To set the level from a verbosity integer directly, without a parsed
`argparse` namespace, use `set_logging_level_by_verbosity`:

```python
# positive raises detail, negative lowers it
kamilog.set_logging_level_by_verbosity(2)

kamilog.set_logging_level_by_verbosity(2, logger_name="myapp")

log = kamilog.getLogger("myapp")
kamilog.set_logging_level_by_verbosity(2, logger=log)
```













### Verbosity-to-Level Mapping

| Flags | Verbosity | Level | Number | Shows |
|---|---|---|---|---|
| `-vvv` or more | ≥ 3 | `DEBUG` | 10 | DEBUG, 〃 |
| `-vv` | 2 | `ENTER` | 15 | ENTER, SKIP, SUCC, 〃 |
| `-v` | 1 | `INFO` | 20 | INFO, PASS, 〃 |
| *(none)* | 0 | `DONE` | 25 | DONE, 〃 |
| `-q` | -1 | `WARN` | 30 | WARN, 〃 |
| `-qq` | -2 | `ERROR` | 40 | ERROR, FAIL, 〃 |
| `-qqq` or more | ≤ -3 | `CRIT` | 50 | CRIT |



### Calculation Only

`set_logging_level_by_namespace` and `set_logging_level_by_verbosity` set a
logger's level as a side effect. To get the offset or the level back as a
plain value instead — for logging, testing, or passing along elsewhere — use
`calc_verbosity` and `calc_logging_level` directly:

```python
# apply a namespace's -v/-q counts to a base verbosity, without touching a logger
verbosity = kamilog.calc_verbosity(args, verbosity=-2)

# map a verbosity integer to a logging level
level = kamilog.calc_logging_level(2)  # ENTER

# or fold a namespace's offset into the same call
level = kamilog.calc_logging_level(-2, namespace=args)
```

`set_logging_level_by_namespace(args, verbosity=v)` is equivalent to
`logger.setLevel(kamilog.calc_logging_level(v, namespace=args))`.
