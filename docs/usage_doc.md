# kamilog Usage Documentation

## Logging

Use `kamilog.getLogger()` in place of `logging.getLogger()` to get a
configured logger instance:

```python
import logging
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

Output:

```
14:30:00 [DEBUG] myapp:    Debugging details here
14:30:00 [INFO ] myapp:    Informational message
14:30:00 [WARN ] myapp:    Warning message
14:30:01 [ERROR] myapp:    Error occurred!
14:30:01 [CRIT ] myapp:    Critical issue!
14:30:01 [ERROR] myapp:    division by zero
Traceback (most recent call last):
  File "main.py", line 12, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

Logger name (`myapp:`) is omitted when `name` is `None` or `"root"`.

All standard and custom log levels are available directly on `kamilog`,
so `import logging` is not needed just for level constants:

| Constant | Number |
|---|---|
| `kamilog.NOTSET` | 0 |
| `kamilog.DEBUG` | 10 |
| `kamilog.ENTER` | 11 |
| `kamilog.SKIP` | 12 |
| `kamilog.INFO` | 20 |
| `kamilog.PASS` | 25 |
| `kamilog.WARNING` | 30 |
| `kamilog.ERROR` | 40 |
| `kamilog.FAIL` | 45 |
| `kamilog.CRITICAL` | 50 |













### Custom Log Levels

`KamiLogger` adds four levels for hook and test-case workflows:

| Method | Constant | Number | Meaning |
|---|---|---|---|
| `log.enter(msg)` | `kamilog.ENTER` | 11 | entering a hook or test case |
| `log.skip(msg)` | `kamilog.SKIP` | 12 | skipping a hook or test case |
| `log.pass_(msg)` | `kamilog.PASS` | 25 | hook or test case passed |
| `log.fail(msg)` | `kamilog.FAIL` | 45 | hook or test case failed |

```python
log.enter("starting setup hook")
log.skip("skipping slow test")
log.pass_("assertion passed")
log.fail("assertion failed")
```

> [!NOTE]
> `pass_` uses a trailing underscore because `pass` is a Python keyword.

































## Logger Settings

#### ANSI Color Output

Color is enabled automatically when stdout/stderr is a TTY, and suppressed
when output is piped or redirected to a file.

Level-to-color mapping (16-color ANSI):

| Level | Color |
|---|---|
| `DEBUG` | Cyan |
| `ENTER` | Bright Green |
| `SKIP` | Green |
| `INFO` | Bright Cyan |
| `PASS` | Bold Green |
| `WARN` | Yellow |
| `ERROR` | Red |
| `FAIL` | Bold Red |
| `CRIT` | Bold Yellow (orange) |

Only the level name `[LEVEL]` is colored. The datetime and source name are
rendered in dim black; the message is uncolored.













### Timestamp Format

By default, only the time is shown (`HH:MM:SS`). Pass `datefmt` to change
the format:

| Constant | Value | Output |
|---|---|---|
| `DATEFMT_TIME` | `"%H:%M:%S"` | `14:30:00` |
| `DATEFMT_TIME_MS` | `"%H:%M:%S.{ms}"` | `14:30:00.123` |
| `DATEFMT_DATETIME` | `"%Y-%m-%d %H:%M:%S"` | `2026-06-15 14:30:00` |
| `DATEFMT_DATETIME_MS` | `"%Y-%m-%d %H:%M:%S.{ms}"` | `2026-06-15 14:30:00.123` |

```python
log = kamilog.getLogger("myapp")
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_TIME_MS)
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_DATETIME)
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_DATETIME_MS)
```

```
14:30:00 [INFO ] myapp:     message
14:30:00.123 [INFO ] myapp: message
2026-06-15 14:30:00 [INFO ] myapp:     message
2026-06-15 14:30:00.123 [INFO ] myapp: message
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
| _(none)_ | 0 | `WARNING` | 30 |
| `-q` or more | ≤ -1 | all suppressed | 51 |

Alternatively, read the verbosity value as an integer:

```python
print(kamilog.calc_verbosity(args))  # e.g. 1
```
