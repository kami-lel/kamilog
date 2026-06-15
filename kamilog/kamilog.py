"""
kamilog: Customized Logging Output Module

Provides Python loggers with structured output, custom log levels,
ANSI 16-color support, and flexible timestamp options.

Q.v. https://github.com/kami-lel/kamilog
"""

import logging
import sys
from logging import Formatter, StreamHandler

__version__ = "1.2.1-alpha"
__author__ = "kamiLeL"

__all__ = (
    "getLogger",
    "KamiLogger",
    "add_verbose_arguments",
    "calc_verbosity",
    "set_logging_level_by_verbosity",
    # log levels
    "NOTSET",
    "DEBUG",
    "ENTER",
    "SKIP",
    "INFO",
    "PASS",
    "WARNING",
    "ERROR",
    "FAIL",
    "CRITICAL",
    # datetime format constants
    "DATEFMT_TIME",
    "DATEFMT_TIME_MS",
    "DATEFMT_DATETIME",
    "DATEFMT_DATETIME_MS",
)


# constants  ###################################################################

# log level constants  =========================================================

NOTSET = logging.NOTSET  # 0
DEBUG = logging.DEBUG  # 10
INFO = logging.INFO  # 20
WARNING = logging.WARNING  # 30
ERROR = logging.ERROR  # 40
CRITICAL = logging.CRITICAL  # 50

# customized logging level

ENTER = 11
SKIP = 12
PASS = 25
FAIL = 45


# Date Time Format  ============================================================
DATEFMT_TIME = "%H:%M:%S"
DATEFMT_TIME_MS = "%H:%M:%S.{ms}"
DATEFMT_DATETIME = "%Y-%m-%d %H:%M:%S"
DATEFMT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.{ms}"


# set up logging  ##############################################################
logging.addLevelName(ENTER, "ENTER")
logging.addLevelName(SKIP, "SKIP")
logging.addLevelName(PASS, "PASS")
logging.addLevelName(FAIL, "FAIL")


# Customized Logging  ##########################################################
class KamiLogger(logging.Logger):  # ===========================================
    """Logger subclass extending :class:`logging.Logger` with four additional levels.

    Custom levels (in numeric order between standard ones):

    - ``ENTER`` (11): entering a hook or test case
    - ``SKIP``  (12): skipping a hook or test case
    - ``PASS``  (25): hook or test case passed
    - ``FAIL``  (45): hook or test case failed

    Use :func:`getLogger` to obtain a configured instance.
    """

    def enter(self, message, *args, **kwargs):
        """
        Log at ``ENTER`` level (11): entering a hook or test case.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(ENTER):
            self._log(ENTER, message, args, stacklevel=2, **kwargs)

    def skip(self, message, *args, **kwargs):
        """
        Log at ``SKIP`` level (12): skipping a hook or test case.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(SKIP):
            self._log(SKIP, message, args, stacklevel=2, **kwargs)

    def pass_(self, message, *args, **kwargs):
        """
        Log at ``PASS`` level (25): hook or test case passed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(PASS):
            self._log(PASS, message, args, stacklevel=2, **kwargs)

    def fail(self, message, *args, **kwargs):
        """
        Log at ``FAIL`` level (45): hook or test case failed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(FAIL):
            self._log(FAIL, message, args, stacklevel=2, **kwargs)


logging.setLoggerClass(KamiLogger)
# root logger exists before setLoggerClass — patch its class directly
logging.root.__class__ = KamiLogger


# log formatter   ==============================================================


_PADDED_LEVELNAME_MAP = {
    logging.DEBUG: "DEBUG",
    ENTER: "ENTER",
    SKIP: "SKIP ",
    logging.INFO: "INFO ",
    PASS: "PASS ",
    logging.WARNING: "WARN ",
    logging.ERROR: "ERROR",
    FAIL: "FAIL ",
    logging.CRITICAL: "CRIT ",
}


_ANSI_RESET = "\033[0m"
_ANSI_DATETIME = "\033[30m"
_ANSI_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",  # cyan
    ENTER: "\033[92m",  # bright green
    SKIP: "\033[32m",  # green
    logging.INFO: "\033[96m",  # bright cyan
    PASS: "\033[1;32m",  # bold green
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    FAIL: "\033[1;31m",  # bold red
    logging.CRITICAL: "\033[1;33m",  # bold yellow (orange)
}


class _LogFormatter(Formatter):
    """
    internal log formatter producing structured, optionally colored output
    """

    def __init__(
        self, *, use_color=False, datefmt=DATEFMT_TIME, relative_to=None
    ):
        """
        :param use_color: enable ANSI color output
        :type use_color: bool
        :param datefmt: strftime format for wall-clock timestamps;
                ignored when ``relative_to`` is set; defaults to ``DATEFMT_TIME``
        :type datefmt: str
        :param relative_to: Unix timestamp used as epoch for relative time display;
                mutually exclusive with ``datefmt``
        :type relative_to: float, optional
        """
        super().__init__(datefmt=datefmt)
        self.use_color = use_color
        self._datefmt = datefmt
        self._relative_to = relative_to

    # helpers  =================================================================

    @staticmethod
    def _levelno2padded_levelname(levelno):
        """
        :param levelno: numeric logging level
        :type levelno: int
        :return: 5-character padded level name; falls back to the numeric value for unknown levels
        :rtype: str
        """
        return _PADDED_LEVELNAME_MAP.get(levelno, str(levelno).ljust(5)[:5])

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
        padded = self._levelno2padded_levelname(levelno)
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

    # extend Formatter  ========================================================

    def formatTime(self, record, datefmt=None):
        """
        :param record: log record
        :type record: logging.LogRecord
        :param datefmt: strftime format override; falls back to ``_datefmt`` if omitted
        :type datefmt: str, optional
        :return: formatted and optionally colored timestamp string
        :rtype: str
        """
        if self._relative_to is not None:
            asctime = self._fmt_relative(record.created)
        else:
            asctime = super().formatTime(record, datefmt or self._datefmt)
            asctime = asctime.replace(
                "{ms}", "{:03d}".format(int(record.msecs))
            )
        return self._fmt_asctime(asctime)

    def format(self, record):
        """
        :param record: log record
        :type record: logging.LogRecord
        :return: fully formatted log line: timestamp, level, optional source, message
        :rtype: str
        """
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
            result = "{}\n{}".format(
                result, self.formatStack(record.stack_info)
            )

        return result


# get logger  ##################################################################


# pylint: disable-next=invalid-name
def getLogger(name=None, *, datefmt=DATEFMT_TIME, relative_to=None):
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
        stdout_handler.setFormatter(
            _LogFormatter(
                use_color=sys.stdout.isatty(),
                datefmt=datefmt,
                relative_to=relative_to,
            )
        )
        stdout_handler.addFilter(lambda r: r.levelno < logging.WARNING)

        stderr_handler = StreamHandler(sys.stderr)
        stderr_handler.setFormatter(
            _LogFormatter(
                use_color=sys.stderr.isatty(),
                datefmt=datefmt,
                relative_to=relative_to,
            )
        )
        stderr_handler.addFilter(lambda r: r.levelno >= logging.WARNING)

        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

    return logger


# verbosity & logging level  ###################################################


def add_verbose_arguments(parser):
    """
    Add ``-v``/``--verbose`` and ``-q``/``--quiet`` options to ``parser``.

    Each ``-v`` increases verbosity by 1; each ``-q`` decreases by 1.

    :param parser: argument parser to extend
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
    Calculate a verbosity integer from ``--verbose`` and ``--quiet`` counts.

    Verbosity defaults to 0; each ``-v`` adds 1, each ``-q`` subtracts 1.
    There are no upper or lower bounds.

    :param namespace: parsed namespace containing ``verbose`` and/or ``quiet`` counts
    :type namespace: argparse.Namespace
    :return: net verbosity level
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
    Set the logging level of a logger based on verbosity flags.

    Verbosity-to-level mapping:

    - ``-vv`` or more: ``DEBUG``
    - ``-v``: ``INFO``
    - no flags: ``WARNING``
    - ``-q`` or more: all output suppressed (level above ``CRITICAL``)

    :param namespace: parsed namespace containing ``--verbose`` and/or ``--quiet`` counts
    :type namespace: argparse.Namespace
    :param logger_name: name of logger to configure; ``None`` targets the root logger
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
