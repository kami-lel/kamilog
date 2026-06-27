"""
kamilog: Customized Logging Output Module

Provides Python loggers with structured output, custom log levels,
ANSI 16-color support, and flexible timestamp options.

Q.v. https://github.com/kami-lel/kamilog
"""

import logging
import sys
from collections import deque
from enum import IntEnum
from logging import Formatter, StreamHandler

__version__ = "1.4.2"
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
    "SUCC",
    "DONE",
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


# log levels  ==================================================================

NOTSET = logging.NOTSET  # 0
DEBUG = logging.DEBUG  # 10
INFO = logging.INFO  # 20
WARNING = logging.WARNING  # 30
ERROR = logging.ERROR  # 40
CRITICAL = logging.CRITICAL  # 50


class _CustomLogLevel(IntEnum):
    """custom log level with padded display name."""

    def __new__(cls, value, display):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.display = display
        return obj

    ENTER = (11, "ENTER")
    SKIP = (12, "SKIP ")
    PASS = (21, "PASS ")
    SUCC = (22, "SUCC.")
    DONE = (25, "DONE ")
    FAIL = (45, "FAIL ")


ENTER = _CustomLogLevel.ENTER
SKIP = _CustomLogLevel.SKIP
PASS = _CustomLogLevel.PASS
SUCC = _CustomLogLevel.SUCC
DONE = _CustomLogLevel.DONE
FAIL = _CustomLogLevel.FAIL


# datetime formats  ============================================================
DATEFMT_TIME = "%H:%M:%S"
DATEFMT_TIME_MS = "%H:%M:%S.{ms}"
DATEFMT_DATETIME = "%Y-%m-%d %H:%M:%S"
DATEFMT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.{ms}"


# registration  ================================================================

for _lvl in _CustomLogLevel:
    logging.addLevelName(int(_lvl), _lvl.name)


# KamiLogger  ##################################################################


class KamiLogger(logging.Logger):
    """
    Logger subclass extending :class:`logging.Logger` with six additional levels.

    Custom levels (in numeric order between standard ones):

    - ``ENTER`` (11): entering a hook or test case
    - ``SKIP``  (12): skipping a hook or test case
    - ``PASS``  (21): hook or test case passed
    - ``SUCC``  (22): task or operation succeeded
    - ``DONE``  (25): task or operation completed
    - ``FAIL``  (45): hook or test case failed

    Use :func:`getLogger` to obtain a configured instance.
    """

    def enter(self, message, *args, **kwargs):
        """
        Log at ``ENTER`` level (11): entering a hook or test case.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.ENTER):
            self._log(_CustomLogLevel.ENTER, message, args, stacklevel=2, **kwargs)

    def skip(self, message, *args, **kwargs):
        """
        Log at ``SKIP`` level (12): skipping a hook or test case.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.SKIP):
            self._log(_CustomLogLevel.SKIP, message, args, stacklevel=2, **kwargs)

    def pass_(self, message, *args, **kwargs):
        """
        Log at ``PASS`` level (21): hook or test case passed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.PASS):
            self._log(_CustomLogLevel.PASS, message, args, stacklevel=2, **kwargs)

    def succ(self, message, *args, **kwargs):
        """
        Log at ``SUCC`` level (22): task or operation succeeded.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.SUCC):
            self._log(_CustomLogLevel.SUCC, message, args, stacklevel=2, **kwargs)

    def done(self, message, *args, **kwargs):
        """
        Log at ``DONE`` level (25): task or operation completed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.DONE):
            self._log(_CustomLogLevel.DONE, message, args, stacklevel=2, **kwargs)

    def fail(self, message, *args, **kwargs):
        """
        Log at ``FAIL`` level (45): hook or test case failed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.FAIL):
            self._log(_CustomLogLevel.FAIL, message, args, stacklevel=2, **kwargs)


logging.setLoggerClass(KamiLogger)
# root logger exists before setLoggerClass — patch its class directly
logging.root.__class__ = KamiLogger


# _LogFormatter  ###############################################################


# formatting tables  ===========================================================

_PADDED_LEVELNAME_MAP = {
    logging.DEBUG: "DEBUG",
    _CustomLogLevel.ENTER: _CustomLogLevel.ENTER.display,
    _CustomLogLevel.SKIP: _CustomLogLevel.SKIP.display,
    logging.INFO: "INFO ",
    _CustomLogLevel.PASS: _CustomLogLevel.PASS.display,
    _CustomLogLevel.SUCC: _CustomLogLevel.SUCC.display,
    _CustomLogLevel.DONE: _CustomLogLevel.DONE.display,
    logging.WARNING: "WARN.",
    logging.ERROR: "ERROR",
    _CustomLogLevel.FAIL: _CustomLogLevel.FAIL.display,
    logging.CRITICAL: "CRIT.",
}


_ANSI_RESET = "\033[0m"
_ANSI_BOLD = "\033[1m"
_ANSI_DATETIME = "\033[90m"  # bright black (grey)
_ANSI_SOURCE = "\033[90m"  # bright black (grey)
_ANSI_LEVEL_COLORS = {
    logging.DEBUG: "\033[34m",  # blue
    _CustomLogLevel.ENTER: "\033[94m",  # bright blue
    _CustomLogLevel.SKIP: "\033[36m",  # cyan
    logging.INFO: "\033[96m",  # bright cyan
    _CustomLogLevel.PASS: "\033[32m",  # green
    _CustomLogLevel.SUCC: "\033[92m",  # bright green
    _CustomLogLevel.DONE: "\033[93m",  # bright yellow
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    _CustomLogLevel.FAIL: "\033[91m",  # bright red
    logging.CRITICAL: "\033[95m",  # bright magenta
}


class _LogFormatter(Formatter):
    """
    internal log formatter producing structured, optionally colored output
    """

    def __init__(self, *, use_color=False, datefmt=None, relative_to=None):
        """
        :param use_color: enable ANSI color output
        :type use_color: bool
        :param datefmt: strftime format for wall-clock timestamps;
                ignored when ``relative_to`` is set; defaults to ``None`` (no timestamp)
        :type datefmt: str, optional
        :param relative_to: Unix timestamp used as epoch for relative time display;
                mutually exclusive with ``datefmt``
        :type relative_to: float, optional
        """
        super().__init__(datefmt=datefmt)
        self.use_color = use_color
        self._datefmt = datefmt
        self._relative_to = relative_to

    # helpers  =================================================================

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
        :return: level name without brackets, e.g. ``DEBUG``, colored and bold if enabled
        :rtype: str
        """
        padded = _PADDED_LEVELNAME_MAP.get(levelno, str(levelno).ljust(5)[:5])
        if self.use_color:
            color = _ANSI_LEVEL_COLORS.get(levelno, "")
            return "{}{}{}{}".format(_ANSI_BOLD, color, padded, _ANSI_RESET)
        return padded

    def _fmt_source(self, name):
        """
        :param name: logger name
        :type name: str
        :return: ``"name:"`` with the name in bold black, or ``":"`` in black if name is root or absent
        :rtype: str
        """
        if not name or name == "root":
            if self.use_color:
                return "{}:{}".format(_ANSI_DATETIME, _ANSI_RESET)
            return ":"
        if self.use_color:
            return "{}{}{}{}:{}".format(
                _ANSI_SOURCE, name, _ANSI_RESET, _ANSI_DATETIME, _ANSI_RESET
            )
        return "{}:".format(name)

    def _fmt_relative(self, created):
        """
        :param created: Unix timestamp of the log record
        :type created: float
        :return: elapsed time since ``_relative_to`` as ``+HH:MM:SS.mmm`` or ``-HH:MM:SS.mmm``
        :rtype: str
        """
        delta = created - self._relative_to
        sign = "-" if delta < 0 else "+"
        delta = abs(delta)
        h, rem = divmod(int(delta), 3600)
        m, s = divmod(rem, 60)
        ms = int((delta % 1) * 1000)
        return "{}{:02d}:{:02d}:{:02d}.{:03d}".format(sign, h, m, s, ms)

    # extend Formatter  ========================================================

    def formatTime(self, record, datefmt=None):
        """
        :param record: log record
        :type record: logging.LogRecord
        :param datefmt: strftime format override; falls back to ``_datefmt`` if omitted
        :type datefmt: str, optional
        :return: formatted and optionally colored timestamp string, or empty string if no timestamp
        :rtype: str
        """
        if self._relative_to is not None:
            asctime = self._fmt_relative(record.created)
            return self._fmt_asctime(asctime)
        elif datefmt or self._datefmt:
            asctime = super().formatTime(record, datefmt or self._datefmt)
            asctime = asctime.replace(
                "{ms}", "{:03d}".format(int(record.msecs))
            )
            return self._fmt_asctime(asctime)
        else:
            return ""

    def format(self, record):
        """
        :param record: log record
        :type record: logging.LogRecord
        :return: fully formatted log line: optional timestamp, level, source (or colon), message
        :rtype: str
        """
        record = logging.makeLogRecord(record.__dict__)

        asctime = self.formatTime(record)
        source = self._fmt_source(record.name)
        space = " " if record.name and record.name != "root" else ""

        if asctime:
            result = "{} {}{}{} {}".format(
                asctime,
                self._fmt_level(record.levelno),
                space,
                source,
                record.getMessage(),
            )
        else:
            result = "{}{}{} {}".format(
                self._fmt_level(record.levelno),
                space,
                source,
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


# _DiffOnlyMsgFilter  ##########################################################


class _DiffOnlyMsgFilter(logging.Filter):
    """
    suppress characters shared across the last ``window`` messages, so
    repeated log lines collapse down to only what changed.

    compares each incoming message against a sliding window of prior
    messages; positions that are identical in all of them are candidates
    for compression. contiguous common runs are replaced with ``〃\\t``
    markers in multiples of 8: each group of 8 common chars becomes one
    ``〃\\t`` pair. at least 2 original chars are preserved at each end of
    the compressed block, giving visual context around the marker.


    :param window: number of prior messages held for comparison;
            suppression activates once this many messages have been seen
    :type window: int
    """

    def __init__(self, window=3):
        super().__init__()
        self._history = deque(maxlen=window)
        # _common[i] = shared char at position i across all history,
        # or None where messages diverge or lengths differ
        self._common: list = []

    def _update_common(self):
        """
        recompute _common from current _history
        """
        history = list(self._history)
        if not history:
            self._common = []
            return
        min_len = min(len(s) for s in history)
        max_len = max(len(s) for s in history)
        common: list = []
        for i in range(max_len):
            if i >= min_len:
                common.append(None)  # position missing in some messages
            else:
                ch = history[0][i]
                common.append(
                    ch if all(s[i] == ch for s in history[1:]) else None
                )
        self._common = common

    def filter(self, record):
        """
        :param record: log record to mask in place
        :type record: logging.LogRecord
        :return: always ``True``; this filter never drops records
        :rtype: bool
        """
        message = record.getMessage()

        if len(self._history) == self._history.maxlen:
            common = self._common
            # mark positions where current message matches all history
            n_common = len(common)
            is_common = [
                i < n_common and common[i] is not None and common[i] == ch
                for i, ch in enumerate(message)
            ]
            # compress common runs: each 8-char block → one tab;
            # keep ≥2 original chars at each end of the compressed block
            result = []
            i = 0
            msg_len = len(message)
            while i < msg_len:
                if not is_common[i]:
                    result.append(message[i])
                    i += 1
                else:
                    run_s = i
                    while i < msg_len and is_common[i]:
                        i += 1
                    run_e = i
                    N = run_e - run_s
                    # leading: chars to keep so ≥2 chars precede the tab
                    leading = max(0, 2 - run_s)
                    replaceable = N - leading - 2  # reserve ≥2 trailing
                    k = replaceable // 8 if replaceable > 0 else 0
                    if k == 0:
                        result.append(message[run_s:run_e])
                    else:
                        tab_s = run_s + leading
                        result.append(message[run_s:tab_s])
                        result.append("〃\t" * k)
                        result.append(message[tab_s + 8 * k : run_e])
            masked = "".join(result)
        else:
            masked = message

        self._history.append(message)
        self._update_common()
        record.msg = masked
        record.args = ()
        return True


# Public API  ##################################################################


# pylint: disable-next=invalid-name
def getLogger(name=None, *, datefmt=None, relative_to=None):
    """
    :param name: logger name
    :type name: str
    :param datefmt: strftime format for timestamps; ignored when ``relative_to`` is set;
            defaults to ``None`` (no timestamp)
    :type datefmt: str, optional
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

    if not any(isinstance(f, _DiffOnlyMsgFilter) for f in logger.filters):
        logger.addFilter(_DiffOnlyMsgFilter())

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


# verbosity helpers  ###########################################################


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


def set_logging_level_by_verbosity(namespace, *, logger=None, logger_name=None):
    """
    Set the logging level of a logger based on verbosity flags.

    Verbosity-to-level mapping:

    - ``-vv`` or more: ``DEBUG`` (10)
    - ``-v``: ``INFO`` (20)
    - no flags: ``DONE`` (25)
    - ``-q``: ``WARNING`` (30)
    - ``-qq``: ``ERROR`` (40)
    - ``-qqq`` or more: ``CRITICAL`` (50)


    :param namespace: parsed namespace containing ``--verbose`` and/or ``--quiet`` counts
    :type namespace: argparse.Namespace
    :param logger: logger instance to configure; takes priority over ``logger_name``
    :type logger: logging.Logger, optional
    :param logger_name: name of logger to configure; ``None`` targets the root logger;
            ignored when ``logger`` is provided
    :type logger_name: str, optional
    """
    verbosity = calc_verbosity(namespace)

    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity == 0:
        level = DONE
    elif verbosity == -1:
        level = logging.WARNING
    elif verbosity == -2:
        level = logging.ERROR
    else:  # verbosity <= -3
        level = logging.CRITICAL

    if logger is None:
        logger = logging.getLogger(logger_name)

    logger.setLevel(level)
