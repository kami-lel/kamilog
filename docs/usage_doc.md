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
log.warning("Warning message")
log.error("Error occurred!")
log.critical("Critical issue!")

try:
    1 / 0
except ZeroDivisionError as err:
    log.exception(err)
```

Default output (no timestamp):

```
DEBUG myapp: Debugging details here
INFO  myapp: Informational message
WARN. myapp: Warning message
ERROR myapp: Error occurred!
CRIT. myapp: Critical issue!
ERROR myapp: division by zero
Traceback (most recent call last):
  File "main.py", line 12, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

Logger name (`myapp:`) is omitted when `name` is `None` or `"root"`.













### Custom Log Levels

<!-- TODO rewrite a single table contains all levels (native & customize), function, level & color -->

`KamiLogger` adds six levels for hook and test-case workflows:

| Method | Constant | Number |
|---|---|---|
| `log.enter(msg)` | `kamilog.ENTER` | 11 |
| `log.skip(msg)` | `kamilog.SKIP` | 12 |
| `log.pass_(msg)` | `kamilog.PASS` | 21 |
| `log.succ(msg)` | `kamilog.SUCC` | 22 |
| `log.done(msg)` | `kamilog.DONE` | 25 |
| `log.fail(msg)` | `kamilog.FAIL` | 45 |

Example output with custom levels:

```python
log = kamilog.getLogger("myapp")
log.setLevel(kamilog.DEBUG)

log.enter("entering setup")      # ENTER myapp: entering setup
log.info("processing data")      # INFO  myapp: processing data
log.pass_("validation passed")   # PASS  myapp: validation passed
log.succ("operation succeeded")  # SUCC. myapp: operation succeeded
log.done("task completed")       # DONE  myapp: task completed
log.fail("task failed")          # FAIL  myapp: task failed
```

> [!NOTE]
> `pass_` uses a trailing underscore because `pass` is a Python keyword.

### All Log Levels

| Function | Meaning |
|---|---|
| `.debug()` | debugging information shown only during development |
| `.enter()` | marks start of a routine; useful for tracking program logic during development |
| `.skip()` | marks skipped portion of routine; useful for tracking program logic during development |
| `.info()` | general informational message related to program function |
| `.pass_()` | test case passed |
| `.succ()` | subroutine or execution succeeded |
| `.done()` | entire program or major component completed successfully |
| `.warning()` | warning condition that should be investigated |
| `.error()` | error condition that prevented operation completion |
| `.fail()` | test case or subroutine/execution failed |
| `.critical()` | program stopping or crashing immediately |

































## Logger Settings

#### ANSI Color Output

Color is enabled automatically when stdout/stderr is a TTY, and suppressed
when output is piped or redirected to a file.

Level-to-color mapping (16-color ANSI):

| Level | Color | ANSI Code |
|---|---|---|
| DEBUG | Blue | `\033[34m` |
| ENTER | Bright Blue | `\033[94m` |
| SKIP  | Cyan | `\033[36m` |
| INFO  | Bright Cyan | `\033[96m` |
| PASS  | Green | `\033[32m` |
| SUCC. | Bright Green | `\033[92m` |
| DONE  | Bright Yellow | `\033[93m` |
| WARN. | Yellow | `\033[33m` |
| ERROR | Red | `\033[31m` |
| FAIL  | Bright Red | `\033[91m` |
| CRIT. | Bright Magenta | `\033[95m` |

Formatting:
- **Timestamp**: bright black (grey)
- **Level name**: colored (by table) and bold
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
INFO  sensor: te〃\tture=21.6 humidity=55% status=OK
INFO  sensor: te〃\tture=21.9 humidity=55% status=OK
```

The filter is invisible during a warmup period (first 3 messages) and resets automatically when the message pattern changes.

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
| `-vv` or more | ≥ 2 | `DEBUG` | 10 |
| `-v` | 1 | `INFO` | 20 |
| _(none)_ | 0 | `DONE` | 25 |
| `-q` | -1 | `WARNING` | 30 |
| `-qq` | -2 | `ERROR` | 40 |
| `-qqq` or more | ≤ -3 | `CRITICAL` | 50 |

Alternatively, read the verbosity value as an integer:

```python
print(kamilog.calc_verbosity(args))  # e.g. 1
```
