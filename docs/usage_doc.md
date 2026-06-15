# kamilog Usage Documentation

## Basic Logging

Use `kamilog.getLogger()` (in places of `logging.getLogger()`)
to get a configured logger instance

```python
import logging
import kamilog

my_logger = kamilog.getLogger("myLogger")
my_logger.setLevel(logging.DEBUG)

my_logger.debug("Debugging details here")
my_logger.info("Informational message")
my_logger.warning("Warning message")
my_logger.error("Error occurred!")
my_logger.critical("Critical issue!")

try:
    1 / 0
except ZeroDivisionError as err:
    my_logger.exception(err)
```

Output:

```
[2024-06-15 14:30:00,000] DEBUG: Debugging details here
[2024-06-15 14:30:00,000] INFO : Informational message
[2024-06-15 14:30:00,000] WARN : Warning message
[2024-06-15 14:30:00,001] ERROR: Error occurred!
[2024-06-15 14:30:00,001] CRIT : Critical issue!
[2024-06-15 14:30:00,001] ERROR: division by zero
Traceback (most recent call last):
  File "/home/kami/repos/kami-log-py/example.py", line 18, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

## Verbosity and Logging Level

Set up parser with options of `-v/--verbose` and `-q/--quiet`:

```python
from argparse import ArgumentParser

parser = ArgumentParser()
add_verbose_arguments(parser)
```

After parsing, set logging level of logger by verbosity of this parser:

```python
args = parser.parse_args()
set_logging_level_by_verbosity(args)
```

Alternatively, calculate and get the verbosity value as a `int`:

```python
print(calc_verbosity(args))  # 1
```
