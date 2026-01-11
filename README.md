# kami-log-py README 📝

<!-- 
todo option to use relative time
todo option to omit date in time
todo include logger name in the message
todo use emoji if console supported
todo use ascii coloring if console supported
todo send to stdout & stderr separately
todo add file handler option for getLogger
Todo use HU to check to AMs are included in files under kamilog
todo install as submodule
todo install as python package
-->

## 🚀 Features

- Custom log message formatting with timestamp and padded log level names
- Padded log levels for consistent and neat alignment ("INFO ", "WARN ", etc.)
- Fully compatible with Python’s native `logging` module for seamless integration
- Ensures that each logger is configured only once to avoid duplicate handlers
- Lightweight, simple to integrate, and easily extensible













## Installation

### 📜 Installation as Script

Copy the single script `./kamilog/kamilog.py` into your project folder.

Example directory structure:

```
your_project/
├── kamilog.py
└── main.py
```

In `main.py`, import the module as follows:

```python
import kamilog
```





### 📦 Installation as Module

Copy the entire `kamilog` folder into your project's source folder.

Example directory structure:

```
your_project/
├── project_abc/
│   ├── kamilog/
│   │   ├── __init__.py
│   │   └── kamilog.py
│   ├── module_a/
│   │   └── some_code.py
│   └── module_b/
│       └── other_code.py
└── setup.py
```

Then you can import `kamilog` anywhere within the project like this:

```python
from project_abc import kamilog
```













## Usage

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




### verbosity and logging level

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