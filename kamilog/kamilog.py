"""kamilog: Customized Logging Output Module

This script provides a simple interface to obtain Python loggers with a
customized logging output format. The format includes timestamps and padded
log level names for cleaner, more uniform log display.





Installation as Script:
Copy the single script `./kamilog/kamilog.py` into your project folder.

Example directory structure::

    your_project/
    ├── kamilog.py
    └── main.py

In `main.py`, import the module as follows::

    import kamilog





Installation as Module:
Copy the entire `kamilog` folder into your project's source folder.

Example directory structure::

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

Then you can import `kamilog` anywhere within the project like this::

    from project_abc import kamilog





Usage:
Use ``kamilog.getLogger()` (in places of `logging.getLogger()`)
to get a configured logger instance::

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

Output::

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



verbosity and logging level:

Set up parser with options of `-v/--verbose` and `-q/--quiet`::

    from argparse import ArgumentParser

    parser = ArgumentParser()
    add_verbose_arguments(parser)

After parsing, set logging level of logger by verbosity of this parser::

    args = parser.parse_args()
    set_logging_level_by_verbosity(args)

Alternatively, calc the verbosity as a number::

    print(calc_verbosity(args))  # 1
"""

import logging
import sys
from logging import Formatter, StreamHandler

__version__ = "1.2.1-alpha"
__author__ = "kamiLeL"
__all__ = (
    "KamiLogger",
    "DATEFMT_TIME",
    "DATEFMT_FULL",
    "getLogger",
    "add_verbose_arguments",
    "calc_verbosity",
    "set_logging_level_by_verbosity",
)


# Todo move docstring into docs
# Fixme organize structure, hide some constant

# customized logger  ###########################################################

DATEFMT_TIME = "%H:%M:%S"
DATEFMT_FULL = "%Y-%m-%d %H:%M:%S"


class KamiLogger(logging.Logger):

    ENTER = 11
    SKIP = 12
    PASS = 25
    FAIL = 45

    def enter(self, message, *args, **kwargs):
        if self.isEnabledFor(self.ENTER):
            self._log(self.ENTER, message, args, stacklevel=2, **kwargs)

    def skip(self, message, *args, **kwargs):
        if self.isEnabledFor(self.SKIP):
            self._log(self.SKIP, message, args, stacklevel=2, **kwargs)

    def pass_(self, message, *args, **kwargs):
        if self.isEnabledFor(self.PASS):
            self._log(self.PASS, message, args, stacklevel=2, **kwargs)

    def fail(self, message, *args, **kwargs):
        if self.isEnabledFor(self.FAIL):
            self._log(self.FAIL, message, args, stacklevel=2, **kwargs)


logging.addLevelName(KamiLogger.ENTER, "ENTER")
logging.addLevelName(KamiLogger.SKIP, "SKIP")
logging.addLevelName(KamiLogger.PASS, "PASS")
logging.addLevelName(KamiLogger.FAIL, "FAIL")

_PADDED_LEVELNAME_MAP = {
    logging.DEBUG: "DEBUG",
    KamiLogger.ENTER: "ENTER",
    KamiLogger.SKIP: "SKIP ",
    logging.INFO: "INFO ",
    KamiLogger.PASS: "PASS ",
    logging.WARNING: "WARN ",
    logging.ERROR: "ERROR",
    KamiLogger.FAIL: "FAIL ",
    logging.CRITICAL: "CRIT ",
}

logging.setLoggerClass(KamiLogger)

# root logger exists before setLoggerClass — patch its class directly
logging.root.__class__ = KamiLogger


def _levelno2padded_levelname(levelno):
    """
    :param levelno:
    :type levelno: int
    :return: padded level name, always 5 letter width
    :rtype: str
    """
    return _PADDED_LEVELNAME_MAP.get(levelno, str(levelno).ljust(5)[:5])


_ANSI_RESET = "\033[0m"
_ANSI_DATETIME = "\033[30m"

_ANSI_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",  # cyan
    KamiLogger.ENTER: "\033[92m",  # bright green
    KamiLogger.SKIP: "\033[32m",  # green
    logging.INFO: "\033[96m",  # bright cyan
    KamiLogger.PASS: "\033[1;32m",  # bold green
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    KamiLogger.FAIL: "\033[1;31m",  # bold red
    logging.CRITICAL: "\033[1;33m",  # bold yellow (orange)
}


class _LogFormatter(Formatter):

    def __init__(self, *, use_color=False, datefmt=DATEFMT_TIME, relative_to=None):
        super().__init__(datefmt=datefmt)
        self.use_color = use_color
        self._datefmt = datefmt
        self._relative_to = relative_to

    def _fmt_asctime(self, asctime):
        """
        :param asctime: pre-formatted datetime string
        :type asctime: str
        :return: asctime wrapped in black ANSI codes, or plain if color disabled
        :rtype: str
        """
        if self.use_color:
            return "{}{}{}".format(_ANSI_DATETIME, asctime, _ANSI_RESET)
        return asctime

    def _fmt_level(self, levelno):
        """
        :param levelno: numeric logging level
        :type levelno: int
        :return: level name in brackets, e.g. ``[DEBUG]``, colored if enabled
        :rtype: str
        """
        padded = _levelno2padded_levelname(levelno)
        if self.use_color:
            color = _ANSI_LEVEL_COLORS.get(levelno, "")
            return "{}[{}]{}".format(color, padded, _ANSI_RESET)
        return "[{}]".format(padded)

    def _fmt_source(self, name):
        """
        :param name: logger name
        :type name: str
        :return: ``" name:"`` in black, or empty string if name is root or absent
        :rtype: str
        """
        if not name or name == "root":
            return ""
        if self.use_color:
            return " {}{}:{}".format(_ANSI_DATETIME, name, _ANSI_RESET)
        return " {}:".format(name)

    def _fmt_relative(self, created):
        """
        :param created: Unix timestamp of the log record
        :type created: float
        :return: elapsed time since ``_relative_to`` as ``+HH:MM:SS.mmm``
        :rtype: str
        """
        delta = created - self._relative_to
        h, rem = divmod(int(delta), 3600)
        m, s = divmod(rem, 60)
        ms = int((delta % 1) * 1000)
        return "+{:02d}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)

    def formatTime(self, record, datefmt=None):
        if self._relative_to is not None:
            asctime = self._fmt_relative(record.created)
        else:
            asctime = super().formatTime(record, datefmt or self._datefmt)
        return self._fmt_asctime(asctime)

    def format(self, record):
        record = logging.makeLogRecord(record.__dict__)

        result = "{} {}{}\t{}".format(
            self.formatTime(record),
            self._fmt_level(record.levelno),
            self._fmt_source(record.name),
            record.getMessage(),
        )

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            result = "{}\n{}".format(result, record.exc_text)
        if record.stack_info:
            result = "{}\n{}".format(result, self.formatStack(record.stack_info))

        return result


def getLogger(name=None, *, datefmt=DATEFMT_TIME, relative_to=None) -> KamiLogger:
    """
    :param name: logger name
    :type name: str
    :param datefmt: strftime format for timestamps; ignored when ``relative_to`` is set;
            defaults to ``DATEFMT_TIME`` (time only)
    :type datefmt: str
    :param relative_to: Unix timestamp to use as epoch for relative time display;
            mutually exclusive with ``datefmt``
    :type relative_to: float, optional
    :return: a logger with the `name`, create if non-existence;
            root logger if `name` is `None`
    :rtype: KamiLogger
    """
    logger = logging.getLogger(name)

    if not isinstance(logger, KamiLogger):
        logger.__class__ = KamiLogger

    if not logger.handlers:
        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(_LogFormatter(
            use_color=sys.stdout.isatty(),
            datefmt=datefmt,
            relative_to=relative_to,
        ))
        stdout_handler.addFilter(lambda r: r.levelno < logging.WARNING)

        stderr_handler = StreamHandler(sys.stderr)
        stderr_handler.setFormatter(_LogFormatter(
            use_color=sys.stderr.isatty(),
            datefmt=datefmt,
            relative_to=relative_to,
        ))
        stderr_handler.addFilter(lambda r: r.levelno >= logging.WARNING)

        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

    return logger


# verbosity & logging level  ###################################################


def add_verbose_arguments(parser):
    """
    add -v/--verbose and -q/--quiet options to ``parser``


    :param parser:
    :type parser: argparse.ArgumentParser
    """
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="make verbose, each -v/--verbose increase verbosity by 1",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="make quiet, each -q/--quiet decrease verbosity by 1",
    )


def calc_verbosity(namespace):
    """
    calculate a **verbosity** value from --verbose &/ --quiet options
    contained in ``namespace``

    verbosity default to 0,
    each -v/--verbose flag will +1 to verbosity,
    each -q/--quiet flag will -1 to verbosity,
    no upper/lower bounds


    :param namespace: parsed from parser with --verbose & --quiet options
    :type namespace: argparse.Namespace
    :return: verbosity number
    :rtype: int
    """
    verbosity = 0

    if hasattr(namespace, "verbose"):
        verbosity += namespace.verbose
    if hasattr(namespace, "quiet"):
        verbosity -= namespace.quiet

    return verbosity


def set_logging_level_by_verbosity(namespace, logger_name=None):
    """
    set **logging level** of a logger based on *verbosity* calculated
    from --verbose &/ --quiet options contained in ``namespace``

    - ``-vv`` (or more): DEBUG
    - ``-v``: INFO
    - no option: WARNING
    - ``-q`` (or more): all message suppressed, even CRITICAL


    :param namespace: parsed from parser with --verbose &/ --quiet
    :type namespace: argparse.Namespace
    :param logger_name: set specific logger with this name
            defaults to None, set root logger
    :type logger_name: str, optional
    """
    verbosity = calc_verbosity(namespace)

    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity == 0:
        level = logging.WARNING
    else:
        level = logging.CRITICAL + 1

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
