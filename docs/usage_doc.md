# kamilog Usage Documentation

## Basic Logging

Use `kamilog.getLogger()` in place of `logging.getLogger()` to get a
configured logger instance:

```python
import logging
import kamilog

log = kamilog.getLogger("myapp")
log.setLevel(logging.DEBUG)

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
  ...
ZeroDivisionError: division by zero
```

Logger name (`myapp:`) is omitted when `name` is `None` or `"root"`.


## Custom Log Levels

`KamiLogger` adds four levels for hook and test-case workflows:

| Method | Level | Meaning |
|---|---|---|
| `log.enter(msg)` | 11 | entering a hook or test case |
| `log.skip(msg)` | 12 | skipping a hook or test case |
| `log.pass_(msg)` | 25 | hook or test case passed |
| `log.fail(msg)` | 45 | hook or test case failed |

```python
log.enter("starting setup hook")
log.skip("skipping slow test")
log.pass_("assertion passed")
log.fail("assertion failed")
```

Note: `pass_` uses a trailing underscore because `pass` is a Python keyword.


## ANSI Color Output

Color is enabled automatically when stdout/stderr is a TTY, and suppressed
when output is piped or redirected.

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


## Timestamp Format

### Time only (default)

```python
log = kamilog.getLogger("myapp")
# output: 14:30:00 [INFO ] myapp:    message
```

### Date and time

```python
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_FULL)
# output: 2026-06-15 14:30:00 [INFO ] myapp:    message
```

### Relative time

Pass a Unix timestamp as `relative_to` to display elapsed time since that
point. `datefmt` is ignored in this mode.

```python
import time
import kamilog

start = time.time()
log = kamilog.getLogger("myapp", relative_to=start)

# output: +00:00:01.234 [INFO ] myapp:    message
```


## Verbosity and Logging Level

Set up a parser with `-v`/`--verbose` and `-q`/`--quiet` options:

```python
from argparse import ArgumentParser
import kamilog

parser = ArgumentParser()
kamilog.add_verbose_arguments(parser)
```

After parsing, set the logging level from verbosity:

```python
args = parser.parse_args()
kamilog.set_logging_level_by_verbosity(args)
```

Verbosity-to-level mapping:

| Flags | Level |
|---|---|
| `-vv` or more | `DEBUG` |
| `-v` | `INFO` |
| _(none)_ | `WARNING` |
| `-q` or more | all suppressed |

Alternatively, read the verbosity value as an integer:

```python
print(kamilog.calc_verbosity(args))  # e.g. 1
```
