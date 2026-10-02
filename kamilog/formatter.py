"""
log line formatting: datetime formats, ``_LogFormatEngine``, ``_LogFormatter``
"""

import logging
import time
from logging import Formatter

from .ansi import AnsiRenderer
from .levels import _CustomLogLevel
from .tab_align import _calc_tab_advance

# Datetime Formats  ============================================================
DATEFMT_TIME = "%H:%M:%S"
DATEFMT_TIME_MS = "%H:%M:%S.{ms}"
DATEFMT_DATETIME = "%Y-%m-%d %H:%M:%S"
DATEFMT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.{ms}"

# marks datefmt as unset, so each destination picks its own dft
_DATEFMT_AUTO = object()


# stdlib levels padded to 5 chars; custom levels carry their own display
_PADDED_LEVELNAME_MAP = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO ",
    logging.WARNING: "WARN.",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRIT.",
    **{lvl: lvl.display for lvl in _CustomLogLevel},
}


class _LogFormatEngine:  # *****************************************************
    """
    core log-line formatting logic, independent of ``logging.Formatter``


    :param palette: color palette controlling ANSI output
    :type palette: _AnsiRenderer
    :param datefmt: strftime format string for wall-clock timestamps;
            ``None`` disables timestamps
    :type datefmt: str or None
    :param relative_to: Unix timestamp used as the epoch for relative
            time display
    :type relative_to: float or None
    """

    def __init__(self, palette, *, datefmt=None, relative_to=None):
        self._palette = palette
        self._datefmt = datefmt
        self._relative_to = relative_to

    # Public API  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def count_prefix_chars(self, record):
        """
        :return: printable character count before the message text of the
                record; with badges, the display column where that text starts
        :rtype: int
        """
        name = record.name
        has_name = self._has_source_name(name)

        if self._relative_to is not None:
            ts_len = len(self._fmt_relative(record.created))
        elif self._datefmt:
            ts_len = len(self._strftime_ms(self._datefmt, record))
        else:
            ts_len = 0

        level_len = 5  # always padded/truncated to 5
        space_len = 1 if has_name else 0
        source_len = len(name) + 1 if has_name else 1  # "name:" or ":"

        col = ts_len + 1 if ts_len else 0
        col += level_len
        badges = getattr(record, "badges", ())
        if badges:
            # source starts on the first tab stop after the badges
            col += 1 + len(" ".join(badges))
            col += _calc_tab_advance(col)
        else:
            col += space_len
        return col + source_len + 1

    def format_time(self, record, datefmt=None):
        """
        :return: timestamp of the record per ``datefmt`` or the engine's own
                format, colored; empty string when timestamps are disabled
        :rtype: str
        """
        if self._relative_to is not None:
            return self._fmt_asctime(self._fmt_relative(record.created))
        elif datefmt or self._datefmt:
            asctime = self._strftime_ms(datefmt or self._datefmt, record)
            return self._fmt_asctime(asctime)
        return ""

    def build_line(self, record):
        """
        :return: main log line of the record, without ``exc_info`` or
                ``stack_info``
        :rtype: str
        """
        asctime = self.format_time(record)
        source = self._fmt_source(record.name)
        space = " " if self._has_source_name(record.name) else ""
        badges = getattr(record, "badges", ())
        # badges sit b/t level & source, source on the next tab stop
        badge_seg = " {}\t".format(self._fmt_badges(badges)) if badges else space
        head = "{} ".format(asctime) if asctime else ""
        return "{}{}{}{} {}".format(
            head,
            self._fmt_level(record.levelno),
            badge_seg,
            source,
            record.getMessage(),
        )

    # helpers  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @staticmethod
    def _has_source_name(name):
        """
        :return: if ``name`` is a real logger name, not empty or root
        :rtype: bool
        """
        return bool(name and name != "root")

    @staticmethod
    def _strftime_ms(fmt, record):
        """
        :return: ``record`` creation time per ``fmt``, ``{ms}`` filled
                with zero-padded milliseconds
        :rtype: str
        """
        return time.strftime(fmt, time.localtime(record.created)).replace(
            "{ms}", "{:03d}".format(int(record.msecs))
        )

    def _fmt_asctime(self, asctime):
        """
        color ``asctime`` grey
        """
        return self._palette.color_grey(asctime)

    def _fmt_level(self, levelno):
        """
        build the padded, colored level-name segment
        """
        padded = _PADDED_LEVELNAME_MAP.get(levelno, str(levelno).ljust(5)[:5])
        return self._palette.color_level(padded, levelno)

    def _fmt_badges(self, badges):
        """
        build the space-separated, colored badge segment
        """
        return " ".join(self._palette.color_badge(b, b) for b in badges)

    def _fmt_source(self, name):
        """
        build the colored source-label segment
        """
        if not self._has_source_name(name):
            return self._palette.color_grey(":")
        return "{}{}".format(
            self._palette.color_grey(name),
            self._palette.color_grey(":"),
        )

    def _fmt_relative(self, created):
        """
        format elapsed time relative to ``_relative_to``
        """
        delta = created - self._relative_to
        sign = "-" if delta < 0 else "+"
        delta = abs(delta)
        h, rem = divmod(int(delta), 3600)
        m, s = divmod(rem, 60)
        ms = int((delta % 1) * 1000)
        return "{}{:02d}:{:02d}:{:02d}.{:03d}".format(sign, h, m, s, ms)


class _LogFormatter(Formatter):  # *********************************************
    """
    ``logging.Formatter`` adapter wrapping ``_LogFormatEngine``


    :param stream: forwarded to ``_AnsiRenderer`` for TTY detection;
            ``None`` disables color
    :type stream: IO or None
    :param datefmt: forwarded to ``_LogFormatEngine``; also passed to
            ``Formatter.__init__`` for stdlib compatibility
    :type datefmt: str or None
    :param relative_to: forwarded to ``_LogFormatEngine``
    :type relative_to: float or None
    :param disable_color: disable color regardless of ``stream``
    :type disable_color: bool
    """

    def __init__(
        self,
        stream=None,
        *,
        datefmt=None,
        relative_to=None,
        disable_color=False,
    ):
        super().__init__(datefmt=datefmt)
        self.palette = AnsiRenderer(stream, is_disabled=disable_color)
        self.engine = _LogFormatEngine(
            self.palette, datefmt=datefmt, relative_to=relative_to
        )

    def formatTime(self, record, datefmt=None):
        """
        :return: timestamp from the engine, honoring the ``datefmt`` override
        :rtype: str
        """
        return self.engine.format_time(record, datefmt)

    def format(self, record):
        """
        :return: complete log line, with ``exc_info`` and ``stack_info``
                appended when present
        :rtype: str
        """
        record = logging.makeLogRecord(record.__dict__)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        result = self.engine.build_line(record)
        if record.exc_text:
            result = "{}\n{}".format(result, record.exc_text)
        if record.stack_info:
            result = "{}\n{}".format(
                result, self.formatStack(record.stack_info)
            )
        return result
