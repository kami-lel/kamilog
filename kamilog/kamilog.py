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

__version__ = "1.5.0"
__author__ = "kamiLeL"

__all__ = (
    "getLogger",
    "KamiLogger",
    "add_verbose_arguments",
    "calc_logging_level_from_verbosity",
    "calc_logging_level_from_verbosity_namespace",
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


# enum  ########################################################################


class _CustomLogLevel(IntEnum):
    """custom log level with padded display name."""

    def __new__(cls, value, display):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.display = display
        return obj

    ENTER = (11, "ENTER")
    SKIP = (12, "SKIP ")
    SUCC = (15, "SUCC.")
    PASS = (21, "PASS ")
    DONE = (25, "DONE ")
    FAIL = (45, "FAIL ")


# level registration during import
for _lvl in _CustomLogLevel:
    logging.addLevelName(int(_lvl), _lvl.name)


# constants  ###################################################################

NOTSET = logging.NOTSET  # 0
DEBUG = logging.DEBUG  # 10
ENTER = _CustomLogLevel.ENTER  # 11
SKIP = _CustomLogLevel.SKIP  # 12
SUCC = _CustomLogLevel.SUCC  # 15
INFO = logging.INFO  # 20
PASS = _CustomLogLevel.PASS  # 21
DONE = _CustomLogLevel.DONE  # 25
WARNING = logging.WARNING  # 30
ERROR = logging.ERROR  # 40
FAIL = _CustomLogLevel.FAIL  # 45
CRITICAL = logging.CRITICAL  # 50


# datetime formats  ============================================================
DATEFMT_TIME = "%H:%M:%S"
DATEFMT_TIME_MS = "%H:%M:%S.{ms}"
DATEFMT_DATETIME = "%Y-%m-%d %H:%M:%S"
DATEFMT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.{ms}"


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
            self._log(
                _CustomLogLevel.ENTER, message, args, stacklevel=2, **kwargs
            )

    def skip(self, message, *args, **kwargs):
        """
        Log at ``SKIP`` level (12): skipping a hook or test case.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.SKIP):
            self._log(
                _CustomLogLevel.SKIP, message, args, stacklevel=2, **kwargs
            )

    def pass_(self, message, *args, **kwargs):
        """
        Log at ``PASS`` level (21): hook or test case passed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.PASS):
            self._log(
                _CustomLogLevel.PASS, message, args, stacklevel=2, **kwargs
            )

    def succ(self, message, *args, **kwargs):
        """
        Log at ``SUCC`` level (22): task or operation succeeded.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.SUCC):
            self._log(
                _CustomLogLevel.SUCC, message, args, stacklevel=2, **kwargs
            )

    def done(self, message, *args, **kwargs):
        """
        Log at ``DONE`` level (25): task or operation completed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.DONE):
            self._log(
                _CustomLogLevel.DONE, message, args, stacklevel=2, **kwargs
            )

    def fail(self, message, *args, **kwargs):
        """
        Log at ``FAIL`` level (45): hook or test case failed.

        :param message: log message
        :type message: str
        """
        if self.isEnabledFor(_CustomLogLevel.FAIL):
            self._log(
                _CustomLogLevel.FAIL, message, args, stacklevel=2, **kwargs
            )


logging.setLoggerClass(KamiLogger)
# root logger exists before setLoggerClass — patch its class directly
logging.root.__class__ = KamiLogger


# _LogFormatter  ###############################################################


_PADDED_LEVELNAME_MAP = {
    logging.DEBUG: "DEBUG",
    _CustomLogLevel.ENTER: _CustomLogLevel.ENTER.display,
    _CustomLogLevel.SKIP: _CustomLogLevel.SKIP.display,
    _CustomLogLevel.SUCC: _CustomLogLevel.SUCC.display,
    logging.INFO: "INFO ",
    _CustomLogLevel.PASS: _CustomLogLevel.PASS.display,
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
    logging.DEBUG: "\033[36m",  # cyan
    _CustomLogLevel.ENTER: "\033[96m",  # bright cyan
    _CustomLogLevel.SKIP: "\033[34m",  # blue
    _CustomLogLevel.SUCC: "\033[32m",  # green
    logging.INFO: "\033[94m",  # bright blue
    _CustomLogLevel.PASS: "\033[92m",  # bright green
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

    # HACK refactorization for better readability

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

    def count_prefix_chars(self, record):
        """
        :param record: log record
        :type record: logging.LogRecord
        :return: number of printable characters before the message text,
                 excluding any ANSI escape codes
        :rtype: int
        """
        name = record.name
        has_name = bool(name and name != "root")

        if self._relative_to is not None:
            ts_len = len(self._fmt_relative(record.created))
        elif self._datefmt:
            plain = Formatter.formatTime(self, record, self._datefmt).replace(
                "{ms}", "{:03d}".format(int(record.msecs))
            )
            ts_len = len(plain)
        else:
            ts_len = 0

        level_len = 5  # always padded/truncated to 5
        space_len = 1 if has_name else 0
        source_len = len(name) + 1 if has_name else 1  # "name:" or ":"

        if ts_len:
            return ts_len + 1 + level_len + space_len + source_len + 1
        return level_len + space_len + source_len + 1

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
            # pylint: disable-next=duplicate-string-formatting-argument
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


# diff only message   ##########################################################


class _DiffOnlyEngine:  # ======================================================
    """
    engine for diff-only compression of log message text.

    maintains a sliding window of prior messages; once the window is
    full, compresses character runs common to all of them into ``〃\\t``
    markers aligned to 8-column boundaries from the rendered line start.
    the formatter needed for prefix-width measurement is resolved lazily
    from the logger's handlers on the first ``process()`` call, so
    handlers need not exist at construction time.


    :param logger: logger whose first ``_LogFormatter`` handler supplies
            the formatter for prefix-width measurement
    :type logger: logging.Logger
    :param window: number of prior messages held for comparison;
            compression activates once this many messages have been seen
    :type window: int
    """

    _COMPRESSION_BLOCK_SIZE = 8
    _PRESERVED_TRAILING_CHARS = 2

    def __init__(self, logger, window=3):
        self._logger = logger
        self._history = deque(maxlen=window)
        # _common[i] = shared char at position i across all history,
        # or None where messages diverge or lengths differ
        self._common: list = []
        self._formatter = None  # resolved lazily on first process() call

    # TODO better way to do this?

    def _resolve_formatter(self):
        """
        find and cache the first ``_LogFormatter`` from logger's handlers
        """
        self._formatter = next(
            (
                h.formatter
                for h in self._logger.handlers
                if isinstance(h.formatter, _LogFormatter)
            ),
            None,
        )

    def _update_common(self):
        """
        recompute ``_common`` from the current ``_history`` window
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

    def _compress(self, record, message):
        """
        compress positions in ``message`` matching ``_common`` into
        ``〃\\t`` markers.

        aligns each marker to the next multiple-of-8 column measured
        from the rendered line start (prefix + message offset); runs
        too short to fit one full block after alignment are kept as-is.


        :param record: log record used to measure the prefix width
        :type record: logging.LogRecord
        :param message: raw message text to compress
        :type message: str
        :return: compressed message string
        :rtype: str
        """
        block = self._COMPRESSION_BLOCK_SIZE
        trail = self._PRESERVED_TRAILING_CHARS
        prefix_len = (
            self._formatter.count_prefix_chars(record)
            if self._formatter is not None
            else 0
        )
        n_common = len(self._common)
        is_common = [
            i < n_common
            and self._common[i] is not None
            and self._common[i] == ch
            for i, ch in enumerate(message)
        ]
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
                col_offset = (prefix_len + run_s) % block
                padding = (block - col_offset) % block
                tab_s = run_s + padding
                replaceable = run_e - tab_s - trail
                k = replaceable // block if replaceable > 0 else 0
                if k == 0:
                    result.append(message[run_s:run_e])
                else:
                    result.append(message[run_s:tab_s])
                    result.append("〃\t" * k)
                    result.append(message[tab_s + block * k : run_e])
        return "".join(result)

    def process(self, record):
        """
        process ``record`` and return the (possibly compressed) message.

        if the history window is not yet full, the raw message is
        returned unchanged. once full, character positions common to
        all history messages are compressed into ``〃\\t`` markers.


        :param record: log record being processed
        :type record: logging.LogRecord
        :return: compressed message, or the original during warmup
        :rtype: str
        """
        message = record.getMessage()

        if len(self._history) == self._history.maxlen:
            if self._formatter is None:
                self._resolve_formatter()
            masked = self._compress(record, message)
        else:
            masked = message

        self._history.append(message)
        self._update_common()
        return masked


class _DiffOnlyMsgFilter(logging.Filter):  # ===================================
    """
    ``logging.Filter`` adapter that applies ``_DiffOnlyEngine`` to records.

    delegates all compression logic to an internal ``_DiffOnlyEngine``
    instance; ``filter()`` mutates ``record.msg`` in place with the
    result.


    :param logger: forwarded to ``_DiffOnlyEngine`` for formatter
            resolution
    :type logger: logging.Logger
    :param window: forwarded to ``_DiffOnlyEngine`` as the history
            window size
    :type window: int
    """

    def __init__(self, logger, window=3):
        super().__init__()
        self._engine = _DiffOnlyEngine(logger, window)

    def filter(self, record):
        """
        apply diff-only compression to ``record.msg`` in place.


        :param record: log record to mask in place
        :type record: logging.LogRecord
        :return: always ``True``; this filter never drops records
        :rtype: bool
        """
        record.msg = self._engine.process(record)
        record.args = ()
        return True


# verbosity helpers  ###########################################################

# HACK make privates


def calc_logging_level_from_verbosity(verbosity):
    """
    Map a verbosity integer to a logging level.

    - ``3`` or more: ``DEBUG`` (10)
    - ``2``: ``SUCC`` (15)
    - ``1``: ``INFO`` (20)
    - ``0``: ``DONE`` (25)
    - ``-1``: ``WARNING`` (30)
    - ``-2``: ``ERROR`` (40)
    - ``-3`` or less: ``CRITICAL`` (50)

    :param verbosity: net verbosity count (positive = more verbose)
    :type verbosity: int
    :return: logging level constant
    :rtype: int
    """
    if verbosity >= 3:
        return logging.DEBUG
    elif verbosity == 2:
        return SUCC
    elif verbosity == 1:
        return logging.INFO
    elif verbosity == 0:
        return DONE
    elif verbosity == -1:
        return logging.WARNING
    elif verbosity == -2:
        return logging.ERROR
    else:  # verbosity <= -3
        return logging.CRITICAL


def calc_logging_level_from_verbosity_namespace(namespace):
    """
    Extract verbosity from a parsed namespace and return the corresponding
    logging level.

    Verbosity defaults to 0; each ``-v`` adds 1, each ``-q`` subtracts 1.

    :param namespace: parsed namespace containing ``verbose`` and/or ``quiet`` counts
    :type namespace: argparse.Namespace
    :return: logging level constant
    :rtype: int
    """
    verbosity = 0
    if hasattr(namespace, "verbose"):
        verbosity += namespace.verbose
    if hasattr(namespace, "quiet"):
        verbosity -= namespace.quiet
    return calc_logging_level_from_verbosity(verbosity)


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
        logger.addFilter(_DiffOnlyMsgFilter(logger))

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


def set_logging_level_by_verbosity(namespace, *, logger=None, logger_name=None):
    """
    Set the logging level of a logger based on verbosity flags.

    :param namespace: parsed namespace containing ``--verbose`` and/or ``--quiet`` counts
    :type namespace: argparse.Namespace
    :param logger: logger instance to configure; takes priority over ``logger_name``
    :type logger: logging.Logger, optional
    :param logger_name: name of logger to configure; ``None`` targets the root logger;
            ignored when ``logger`` is provided
    :type logger_name: str, optional
    """
    if logger is None:
        logger = logging.getLogger(logger_name)
    logger.setLevel(calc_logging_level_from_verbosity_namespace(namespace))
