"""
``KamiLogger`` and ``getLogger``: the kamilog logging entry point
"""

import logging
import os
import sys
from logging import FileHandler, StreamHandler

from .badges import _normalize_badges
from .diff_only import _DiffOnlyMsgFilter
from .formatter import DATEFMT_DATETIME_MS, _DATEFMT_AUTO, _LogFormatter
from .levels import (
    CAUTION, DONE, ENTER, FAIL, HINT, IMPORTANT, NOTE, PASS, SKIP, SUCC, TIP,
)


class KamiLogger(logging.Logger):  # ===========================================
    """
    logger subclass extending :class:`logging.Logger` with custom levels

    provides convenience methods for test and hook workflows;
    obtain instances via :func:`getlogger`
    """

    # persistent badges; instances shadow this on first set_persistent_badges call
    _persistent_badges = ()

    def enter(self, message, *args, **kwargs):
        """
        log at ``ENTER`` level (15): entering a hook or test case


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(ENTER, message, args, 2, **kwargs)

    def skip(self, message, *args, **kwargs):
        """
        log at ``SKIP`` level (16): skipping a hook or test case


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(SKIP, message, args, 2, **kwargs)

    def succ(self, message, *args, **kwargs):
        """
        log at ``SUCC`` level (17): task or operation succeeded


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(SUCC, message, args, 2, **kwargs)

    def pass_(self, message, *args, **kwargs):
        """
        log at ``PASS`` level (21): hook or test case passed


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(PASS, message, args, 2, **kwargs)

    def note(self, message, *args, **kwargs):
        """
        log at ``NOTE`` level (23): general aside worth noting


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(NOTE, message, args, 2, **kwargs)

    def tip(self, message, *args, **kwargs):
        """
        log at ``TIP`` level (24): actionable suggestion


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(TIP, message, args, 2, **kwargs)

    def done(self, message, *args, **kwargs):
        """
        log at ``DONE`` level (25): task or operation completed


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(DONE, message, args, 2, **kwargs)

    def hint(self, message, *args, **kwargs):
        """
        log at ``HINT`` level (26): subtle, barely-there cue


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(HINT, message, args, 2, **kwargs)

    def important(self, message, *args, **kwargs):
        """
        log at ``IMPORTANT`` level (27): emphasized information


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(IMPORTANT, message, args, 2, **kwargs)

    def caution(self, message, *args, **kwargs):
        """
        log at ``CAUTION`` level (31): risk of a negative outcome


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(CAUTION, message, args, 2, **kwargs)

    def fail(self, message, *args, **kwargs):
        """
        log at ``FAIL`` level (45): hook or test case failed


        :param message: message, or ``%``-style format string for ``args``
        :type message: str
        :param args: values interpolated into ``message``
        :type args: object
        :param kwargs: forwarded to ``logging.Logger._log``: ``exc_info``,
                ``extra``, ``stack_info``, ``badges``, ``is_inheriting_badges``
        :type kwargs: object
        """
        self._log_if_enabled(FAIL, message, args, 2, **kwargs)

    def set_persistent_badges(self, badges=None):
        """
        replace the persistent badges

        an omitted, ``None`` or empty ``badges`` unsets every
        persistent badge; there is no add or remove of a single badge


        :param badges: badge labels for every later record;
                default=None
        :type badges: str or Iterable(str), optional
        """
        self._persistent_badges = _normalize_badges(badges)

    def clear_persistent_badges(self):
        """
        unset every persistent badge
        """
        self._persistent_badges = ()

    def _log_if_enabled(self, level, msg, args, stacklevel, **kwargs):
        """
        log at ``level`` if enabled; ``stacklevel`` counts from the
                method calling this helper, as if it called ``_log``
        """
        if self.isEnabledFor(level):
            self._log(level, msg, args, stacklevel=stacklevel + 1, **kwargs)

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        badges=None,
        is_inheriting_badges=True,
    ):
        """
        stamp the record with its effective badges, then log as usual;
        per-call ``badges`` add to the persistent set unless
        ``is_inheriting_badges`` is false, and the result lands on
        ``record.badges`` as a priority-sorted tuple
        """
        persistent_badges = self._persistent_badges if is_inheriting_badges else ()
        extra = dict(extra) if extra else {}
        extra["badges"] = _normalize_badges(
            (*persistent_badges, *_normalize_badges(badges))
        )
        # +1 skips this frame so caller info stays correct
        super()._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
        )


logging.setLoggerClass(KamiLogger)
# root logger exists before setLoggerClass — patch its class directly
logging.root.__class__ = KamiLogger


# Logger Public API  ===========================================================


def _attach_diff_only_filter(logger, formatter_kwargs, is_disabled):
    """
    attach a diff-only filter to ``logger`` unless it already has one
    """
    if any(isinstance(f, _DiffOnlyMsgFilter) for f in logger.filters):
        return
    logger.addFilter(
        _DiffOnlyMsgFilter(
            _LogFormatter(sys.stdout, **formatter_kwargs),
            disable_diff_only_compression=is_disabled,
        )
    )


def _build_console_handler(stream, formatter_kwargs, level_filter):
    """
    :return: handler on ``stream`` passing only records ``level_filter``
            accepts, formatted for that stream's TTY
    :rtype: logging.StreamHandler
    """
    handler = StreamHandler(stream)
    handler.setFormatter(_LogFormatter(stream, **formatter_kwargs))
    handler.addFilter(level_filter)
    return handler


def _attach_console_handlers(logger, formatter_kwargs):
    """
    attach stdout (below ``WARNING``) and stderr handlers to ``logger``
    unless it already has a console handler
    """
    if any(
        isinstance(h, StreamHandler) and not isinstance(h, FileHandler)
        for h in logger.handlers
    ):
        return
    logger.addHandler(
        _build_console_handler(
            sys.stdout, formatter_kwargs, lambda r: r.levelno < logging.WARNING
        )
    )
    logger.addHandler(
        _build_console_handler(
            sys.stderr,
            formatter_kwargs,
            lambda r: r.levelno >= logging.WARNING,
        )
    )


def _attach_file_handler(logger, filename, file_mode, formatter_kwargs):
    """
    attach a file handler for ``filename`` to ``logger`` unless one
    already targets that file
    """
    target = os.path.abspath(filename)  # same file under any spelling
    if any(
        isinstance(h, FileHandler) and h.baseFilename == target
        for h in logger.handlers
    ):
        return
    file_handler = FileHandler(filename, mode=file_mode, encoding="utf-8")
    file_handler.setFormatter(_LogFormatter(**formatter_kwargs))
    logger.addHandler(file_handler)  # no level split, all levels


# pylint: disable-next=invalid-name
def getLogger(
    name=None,
    *,
    datefmt=_DATEFMT_AUTO,
    relative_to=None,
    disable_color=False,
    disable_diff_only_compression=False,
    filename=None,
    file_mode="a",
    disable_console=False,
    enable_propagate=False,
):
    """
    return a configured :class:`KamiLogger` for ``name``, creating it if
    needed


    :param name: logger name; default=None, the root logger
    :type name: str, optional
    :param datefmt: strftime format for timestamps;
            default depends on the destination: console prints no
            timestamp, the log file uses ``DATEFMT_DATETIME_MS``;
            an explicit value applies to console and file alike,
            ``None`` disables timestamps on both;
            ignored when ``relative_to`` is set
    :type datefmt: str or None, optional
    :param relative_to: Unix timestamp to use as epoch for relative time
            display; mutually exclusive with ``datefmt``; default=None
    :type relative_to: float, optional
    :param disable_color: whether to disable ANSI color on all handlers
            and the diff-only filter; default=False
    :type disable_color: bool, optional
    :param disable_diff_only_compression: whether to turn off diff-only
            compression and pass records through untouched; default=False
    :type disable_diff_only_compression: bool, optional
    :param filename: path to a log file; when set, a file handler using
            the kamilog format is attached, with color always disabled;
            ``None`` attaches no file handler; default=None
    :type filename: str or None, optional
    :param file_mode: open mode for the log file, forwarded to
            ``logging.FileHandler``; default="a" (append)
    :type file_mode: str, optional
    :param disable_console: whether to skip the stdout/stderr handlers,
            yielding a file-only logger; default=False
    :type disable_console: bool, optional
    :param enable_propagate: whether records also propagate to ancestor
            loggers' handlers; default=False
    :type enable_propagate: bool, optional
    :return: the logger named ``name``, created if it does not exist;
            the root logger if ``name`` is ``None``
    :rtype: KamiLogger
    """
    if datefmt is _DATEFMT_AUTO:  # unset: console silent, file full stamp
        console_datefmt, file_datefmt = None, DATEFMT_DATETIME_MS
    else:
        console_datefmt = file_datefmt = datefmt

    logger = logging.getLogger(name)

    if not isinstance(logger, KamiLogger):
        logger.__class__ = KamiLogger

    logger.propagate = enable_propagate

    console_kwargs = {
        "datefmt": console_datefmt,
        "relative_to": relative_to,
        "disable_color": disable_color,
    }
    _attach_diff_only_filter(
        logger, console_kwargs, disable_diff_only_compression
    )
    if not disable_console:
        _attach_console_handlers(logger, console_kwargs)
    if filename is not None:
        file_kwargs = dict(
            console_kwargs, datefmt=file_datefmt, disable_color=True
        )
        _attach_file_handler(logger, filename, file_mode, file_kwargs)

    return logger
