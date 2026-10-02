"""
kamilog.py

Lightweight Python logging wrapper with custom log levels, structured output,
ANSI colored logging, verbosity control, comment banner utilities, and CLI.

Q.v. https://github.com/kami-lel/kamilog for Project Main Page
Q.v. https://github.com/kami-lel/kamilog/tree/main/docs for Documentation
"""

from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    RawDescriptionHelpFormatter,
)
import logging
import os
import shlex
import subprocess
import sys
from collections import namedtuple
from enum import Flag, IntEnum, auto
from logging import FileHandler, StreamHandler
from string import Formatter as _TemplateParser

from .ansi import AnsiRenderer, AnsiStyle
from .badges import _NATIVE_BADGES, _normalize_badges
from .diff_only import _DiffOnlyEngine, _DiffOnlyMsgFilter
from .formatter import (
    DATEFMT_DATETIME, DATEFMT_DATETIME_MS, DATEFMT_TIME, DATEFMT_TIME_MS,
    _DATEFMT_AUTO, _PADDED_LEVELNAME_MAP, _LogFormatEngine, _LogFormatter,
)
from .levels import (
    CAUTION, CRITICAL, DEBUG, DONE, ENTER, ERROR, FAIL, HINT, IMPORTANT,
    INFO, NOTE, NOTSET, PASS, SKIP, SUCC, TIP, WARNING, _CustomLogLevel,
)
from .tab_align import _TabAlignedLine, _calc_tab_advance, _expand_tabs

__all__ = (
    "kamilog_cli_main",
    "getLogger",
    "KamiLogger",
    "add_verbose_arguments",
    "calc_verbosity",
    "calc_logging_level",
    "set_logging_level_by_namespace",
    "set_logging_level_by_verbosity",
    # ANSI style
    "AnsiStyle",
    "AnsiRenderer",
    # log levels
    "NOTSET",
    "DEBUG",
    "ENTER",
    "SKIP",
    "INFO",
    "PASS",
    "SUCC",
    "NOTE",
    "TIP",
    "DONE",
    "HINT",
    "IMPORTANT",
    "WARNING",
    "CAUTION",
    "ERROR",
    "FAIL",
    "CRITICAL",
    # datetime format constants
    "DATEFMT_TIME",
    "DATEFMT_TIME_MS",
    "DATEFMT_DATETIME",
    "DATEFMT_DATETIME_MS",
    # comment banner
    "gen_comment_banner_centered",
    "gen_comment_banner_left_just",
    "gen_comment_banner_right_just",
    "gen_comment_banner_zero",
)


# metadata  ####################################################################
__version__ = "2.10.0"
__author__ = "kamiLeL"


# Custom Logging  ##############################################################

# Deeds  =======================================================================
_Deed = namedtuple(
    "_Deed", ("name", "arg_names", "template", "level", "err_level")
)


# deed → fixed wording & severities; see docs/deed-doc.md
_DEEDS = {
    d.name: d
    for d in (
        _Deed("create_file", ("path",), "create {path}", INFO, ERROR),
        _Deed("owr_file", ("path",), "overwrite {path}", WARNING, ERROR),
        _Deed("append_file", ("path",), "append {path}", INFO, ERROR),
        _Deed(
            "cp_file",
            ("source", "destination"),
            "copy {source} -> {destination}",
            INFO,
            ERROR,
        ),
        _Deed(
            "mv_file",
            ("source", "destination"),
            "move {source} -> {destination}",
            INFO,
            ERROR,
        ),
        _Deed(
            "chmod_file",
            ("path", "mode"),
            "chmod {path} {mode}",
            INFO,
            ERROR,
        ),
        _Deed("rm_file", ("path",), "delete {path}", WARNING, WARNING),
        _Deed("create_dir", ("path",), "create dir {path}", INFO, ERROR),
        _Deed("rm_dir", ("path",), "delete dir {path}", WARNING, WARNING),
        _Deed(
            "pack_files",
            ("source", "archive"),
            "pack {source} -> {archive}",
            INFO,
            ERROR,
        ),
        _Deed(
            "unpack_archive",
            ("archive", "destination"),
            "unpack {archive} -> {destination}",
            INFO,
            ERROR,
        ),
        _Deed(
            "download",
            ("url", "destination"),
            "download {url} -> {destination}",
            INFO,
            ERROR,
        ),
        _Deed(
            "upload",
            ("source", "url"),
            "upload {source} -> {url}",
            INFO,
            ERROR,
        ),
        _Deed("run_command", ("command",), "run {command}", INFO, ERROR),
        _Deed("load_config", ("path",), "load {path}", INFO, ERROR),
        _Deed("save_config", ("path",), "save {path}", INFO, ERROR),
        _Deed("skip_file", ("path",), "skip {path}", SKIP, WARNING),
    )
}


def _stringify_deed_args(args):
    """
    str() each arg once when given, so a later change to the object can not
    alter the line; None stays None and still drops its segment
    """
    return tuple(None if arg is None else str(arg) for arg in args)


def _raise_unexpected_deed_arg(deed, key):
    """
    raise ``TypeError`` for argument ``key`` that ``deed`` does not accept
    """
    raise TypeError(
        "{}() got an unexpected argument '{}'".format(deed.name, key)
    )


def _bind_deed_methods(cls, make_method, qualname_prefix):
    """
    attach one method per deed to ``cls``, built by ``make_method``
    """
    for deed in _DEEDS.values():
        method = make_method(deed)
        method.__name__ = deed.name
        method.__qualname__ = "{}.{}".format(qualname_prefix, deed.name)
        setattr(cls, deed.name, method)


def _render_deed_message(deed, *args, **kwargs):
    """
    render `deed` wording from positional `args` and named `kwargs`;
    an omitted argument drops its segment, e.g. ` -> {destination}`
    """
    if len(args) > len(deed.arg_names):
        raise TypeError(
            "{}() takes at most {} arguments ({} given)".format(
                deed.name, len(deed.arg_names), len(args)
            )
        )
    values = dict(zip(deed.arg_names, args))
    for key, val in kwargs.items():
        if key not in deed.arg_names or key in values:
            _raise_unexpected_deed_arg(deed, key)
        values[key] = val

    # each field carries the literal before it; the 1st literal is the verb
    parts = []
    fields = _TemplateParser().parse(deed.template)
    for i, (literal, field, _, _) in enumerate(fields):
        is_given = values.get(field) is not None
        if i == 0:
            parts.append(literal if is_given else literal.rstrip())
        if is_given:
            if i > 0:
                parts.append(literal)
            parts.append(str(values[field]))
    return "".join(parts).rstrip()


class _DeedHandle:  # **********************************************************
    """
    handle yielded by a tracked deed block, ``with ... as act``;
    exposes :meth:`set` and :meth:`fail` only
    """

    def __init__(self, scope):
        self._scope = scope

    def set(self, **kwargs):
        """
        give arguments known only after the deed started; an argument still
        missing at block exit drops its segment, and a name the deed lacks or
        already got positionally raises ``TypeError``
        """
        self._scope.set_late_args(kwargs)

    def fail(self, detail):
        """
        mark the deed failed without raising, e.g. a bad exit status;
        the failure line reads ``fail to <message>: <detail>``
        and carries no traceback
        """
        self._scope.mark_failed(detail)


class _DeedScope:  # ***********************************************************
    """
    context manager of one tracked deed;
    logs one line at block exit: success, or failure if the block raised
    or the handle marked it failed
    """

    def __init__(self, logger, deed, args, options):
        self._logger = logger
        self._deed = deed
        self._args = args
        self._options = options
        self._late_args = {}
        self._fail_detail = None
        self._is_failed = False

    def __enter__(self):
        return _DeedHandle(self)

    def __exit__(self, exc_type, exc_value, traceback):
        # only Exception counts; KeyboardInterrupt & SystemExit pass silently
        if exc_type is not None:
            if not issubclass(exc_type, Exception):
                return False
            cause = exc_type.__name__
            if str(exc_value):
                cause = "{}: {}".format(cause, exc_value)
            self._log_failure(cause, (exc_type, exc_value, traceback))
            return self._options["suppress"]
        if self._is_failed:
            self._log_failure(self._fail_detail)
        else:
            self._log_success()
        return False

    def set_late_args(self, kwargs):
        """
        record arguments given after entry, validating each name
        """
        for key in kwargs:
            if key not in self._deed.arg_names:
                _raise_unexpected_deed_arg(self._deed, key)
            if self._deed.arg_names.index(key) < len(self._args):
                raise TypeError(
                    "{}() got multiple values for argument '{}'".format(
                        self._deed.name, key
                    )
                )
        values = _stringify_deed_args(kwargs.values())
        self._late_args.update(zip(kwargs, values))

    def mark_failed(self, detail):
        """
        mark the deed failed as a value; no exception involved
        """
        self._is_failed = True
        self._fail_detail = detail

    def _render(self):
        """
        render the deed wording from entry and late arguments
        """
        return _render_deed_message(self._deed, *self._args, **self._late_args)

    def _log_success(self):
        """
        log the success line at the deed's level
        """
        level = self._options["level"]
        level = self._deed.level if level is None else level
        self._emit(level, self._render())

    def _log_failure(self, cause, exc_info=None):
        """
        log `fail to <message>: <cause>`, with traceback if `exc_info`
        """
        err_level = self._options["err_level"]
        err_level = self._deed.err_level if err_level is None else err_level
        message = "fail to {}".format(self._render())
        if cause is not None and str(cause):
            message = "{}: {}".format(message, cause)
        self._emit(err_level, message, exc_info)

    def _emit(self, level, message, exc_info=None):
        """
        log `message`, attributed to the code holding the `with`
        """
        self._logger._log_if_enabled(
            level,
            message,
            (),
            4,
            exc_info=exc_info,
            badges=self._options["badges"],
            is_inheriting_badges=self._options["is_inheriting_badges"],
        )


class _DeedTrack:  # ***********************************************************
    """
    namespace behind ``logger.track``;
    holds one method per deed, each returning a :class:`_DeedScope`
    """

    def __init__(self, logger):
        self._logger = logger


def _make_track_method(deed):
    """
    build the track-form method of `deed` for :class:`_DeedTrack`
    """

    def track_method(
        self,
        *args,
        level=None,
        err_level=None,
        suppress=False,
        badges=None,
        is_inheriting_badges=True
    ):
        args = _stringify_deed_args(args)
        # render once so a bad arg raises at the call, not at block exit
        _render_deed_message(deed, *args)
        options = {
            "level": level,
            "err_level": err_level,
            "suppress": suppress,
            "badges": badges,
            "is_inheriting_badges": is_inheriting_badges,
        }
        return _DeedScope(self._logger, deed, args, options)

    track_method.__doc__ = """
        track the deed ``{template}``: one line is logged when the block
        exits, at ``level`` on success or at ``err_level`` on an
        ``Exception``, which then propagates unless ``suppress``; the block
        yields a handle with ``set(name=value)`` and ``fail(detail)``


        :param args: the deed's own arguments, in order ``{arg_names}``
        :type args: object
        :param level: severity of the success line; default=the deed's level
        :type level: int, optional
        :param err_level: severity of the failure line;
                default=the deed's error level
        :type err_level: int, optional
        :param suppress: whether to swallow the exception after logging it;
                default=False
        :type suppress: bool, optional
        :param badges: badge labels for this record only; default=None
        :type badges: str or Iterable(str), optional
        :param is_inheriting_badges: whether the persistent badges apply to
                this record; default=True
        :type is_inheriting_badges: bool, optional
        :return: context manager logging the outcome at block exit
        """.format(
        template=deed.template, arg_names=", ".join(deed.arg_names)
    )
    return track_method


_bind_deed_methods(_DeedTrack, _make_track_method, "_DeedTrack")


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

    @property
    def track(self):
        """
        track form of the deed methods, e.g. ``with logger.track.cp_file(a, b)``


        :return: namespace whose methods mirror the plain deed methods
        :rtype: _DeedTrack
        """
        return _DeedTrack(self)

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


def _make_deed_method(deed):
    """
    build the plain-form method of `deed` for :class:`KamiLogger`
    """

    def deed_method(
        self, *args, level=None, badges=None, is_inheriting_badges=True
    ):
        level = deed.level if level is None else level
        if self.isEnabledFor(level):
            self._log(
                level,
                _render_deed_message(deed, *args),
                (),
                stacklevel=2,
                badges=badges,
                is_inheriting_badges=is_inheriting_badges,
            )

    deed_method.__doc__ = """
        log the deed ``{template}`` at ``{level}`` level by default


        :param args: the deed's own arguments, in order ``{arg_names}``;
                trailing ones may be omitted
        :type args: object
        :param level: severity of the line; default=the deed's level
        :type level: int, optional
        :param badges: badge labels for this record only; default=None
        :type badges: str or Iterable(str), optional
        :param is_inheriting_badges: whether the persistent badges apply to
                this record; default=True
        :type is_inheriting_badges: bool, optional
        """.format(
        template=deed.template,
        level=logging.getLevelName(deed.level),
        arg_names=", ".join(deed.arg_names),
    )
    return deed_method


_bind_deed_methods(KamiLogger, _make_deed_method, "KamiLogger")


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


# shared parsers  ==============================================================

_common_parser = ArgumentParser(add_help=False)
_newline_group = _common_parser.add_mutually_exclusive_group()
_newline_group.add_argument(
    "-n",
    "--newline",
    dest="newline",
    action="store_true",
    default=None,
    help="always append a trailing newline after output",
)
_newline_group.add_argument(
    "-N",
    "--no-newline",
    dest="newline",
    action="store_false",
    default=None,
    help="never append a trailing newline after output",
)
_no_color_parser = ArgumentParser(add_help=False, parents=[_common_parser])
_no_color_parser.add_argument(
    "-C",
    "--no-color",
    action="store_true",
    help="disable ANSI color output",
)

_line_width_parser = ArgumentParser(add_help=False, parents=[_no_color_parser])
_line_width_parser.add_argument(
    "-w",
    "--line-width",
    type=int,
    default=80,
    metavar="LINE_WIDTH",
    help="total character width of output line; default 80",
)


def _calc_line_end(args, stdin_content=""):
    """
    decide the trailing-newline ``end`` string: stdin's own newline,
    if any, plus one when ``-n`` and none when ``-N``; with neither
    flag the output ends in exactly one newline
    """
    kept = "\n" if stdin_content.endswith("\n") else ""
    if args.newline is True:
        return kept + "\n"
    if args.newline is False:
        return kept
    return "\n"


def _read_stdin_line():
    """
    :return: the next stdin line raw, and without its trailing newline
    :rtype: tuple(str, str)
    """
    raw = sys.stdin.readline()
    return raw, raw.rstrip("\n")


def _print_output(args, text, raw):
    """
    print ``text`` to stdout, ended per ``-n/-N`` and the newline of ``raw``
    """
    print(text, file=sys.stdout, end=_calc_line_end(args, raw))


def _add_subcommand(
    cli_subparser, name, alias, parents, help_text, description, func
):
    """
    :return: new subparser ``name``, with ``func`` as handler unless
            ``None``, and ``alias`` unless empty
    :rtype: argparse.ArgumentParser
    """
    subparser = cli_subparser.add_parser(
        name,
        parents=parents,
        help=help_text,
        description=description,
        formatter_class=RawDescriptionHelpFormatter,
        aliases=[alias] if alias else [],
    )
    if func is not None:
        subparser.set_defaults(func=func)
    return subparser


# logger CLI  ==================================================================


_LOGGER_HELP = "log stdin lines at LEVEL, honoring verbosity threshold"


_LOGGER_DESCRIPTION = _LOGGER_HELP + """

lines are read from stdin, one log record per stdin line;
verbosity threshold decides which records actually print


example:
  echo 'disk full' | kamilog logger error
  echo 'disk full' | kamilog logger error my_module"""

# lowercase level name → numeric level, ascending by severity
_LOGGER_LEVEL_MAP = {
    logging.getLevelName(lvl).lower(): lvl
    for lvl in sorted(
        (DEBUG, INFO, WARNING, ERROR, CRITICAL, *_CustomLogLevel)
    )
}


def _resolve_level_name(name):
    """
    :return: numeric level of the case-insensitive level ``name``;
            ``None`` passes through
    :rtype: int or None
    """
    return None if name is None else _LOGGER_LEVEL_MAP[name.lower()]


# time format Name to strftime string, None disables timestamps
_LOGGER_TIME_FORMAT_MAP = {
    "time": DATEFMT_TIME,
    "time-ms": DATEFMT_TIME_MS,
    "datetime": DATEFMT_DATETIME,
    "datetime-ms": DATEFMT_DATETIME_MS,
    "no-time": None,
}


def _logger_parser_main(args):
    level = _resolve_level_name(args.level)
    datefmt = _LOGGER_TIME_FORMAT_MAP[args.time_format]  # resolve Time fmt
    logger = getLogger(
        args.name,
        datefmt=datefmt,
        disable_color=args.no_color,
        disable_diff_only_compression=args.no_diff_only,
    )
    set_logging_level_by_namespace(
        args, verbosity=args.verbosity, logger=logger
    )
    raw = sys.stdin.read()
    lines = raw.splitlines()
    last_idx = len(lines) - 1
    final_end = _calc_line_end(args, raw)  # final record's own break
    for i, line in enumerate(lines):  # log each stdin Line
        if i == last_idx:  # only the final break is adjustable
            for handler in logger.handlers:
                handler.terminator = final_end
        logger.log(level, line)


def _register_logger_parser(cli_subparser):
    """
    register the ``logger`` subcommand on ``cli_subparser``
    """
    logger_parser = _add_subcommand(
        cli_subparser,
        "logger",
        "l",
        [_no_color_parser],
        _LOGGER_HELP,
        _LOGGER_DESCRIPTION,
        _logger_parser_main,
    )

    logger_parser.add_argument(
        "level",
        choices=list(_LOGGER_LEVEL_MAP),
        help="log level name",
    )
    logger_parser.add_argument(
        "name",
        nargs="?",
        default=None,
        metavar="LOGGER_NAME",
        help="logger name; default=root logger",
    )
    logger_parser.add_argument(
        "-t",
        "--time-format",
        choices=list(_LOGGER_TIME_FORMAT_MAP),
        default="no-time",
        help="timestamp format; default=no-time",
    )

    logger_parser.add_argument(
        "--verbosity",
        type=int,
        default=3,
        metavar="VERBOSITY",
        help="base verbosity offset for level threshold; default=3",
    )
    add_verbose_arguments(logger_parser)

    logger_parser.add_argument(
        "-D",
        "--no-diff-only",
        action="store_true",
        help="disable diff-only message compression",
    )


# Verbosity  ###################################################################

# auxiliaries  =================================================================


def _set_logger_level(level, *, logger=None, logger_name=None):
    """
    set ``level`` on ``logger``, falling back to ``logger_name``
    """
    if logger is None:
        logger = logging.getLogger(logger_name)
    logger.setLevel(level)


# Verbosity Public API  ========================================================

_VERBOSE_FLAG_CHOICES = ("vq", "VQ", "")
_EXTREME_VERBOSITY = 1_000_000

_STEP_VERBOSE_HELP = "increase verbosity by 1 per {opt}"
_STEP_QUIET_HELP = "decrease verbosity by 1 per {opt}"
_EXTREMITY_VERBOSE_HELP = "set maximally verbose"
_EXTREMITY_QUIET_HELP = "set maximally quiet"


def _flag_option_strings(short_flag, long_flag):
    """
    :return: ``[long_flag]``, or ``["-{short_flag}", long_flag]`` when
            ``short_flag`` is truthy
    :rtype: list[str]
    """
    if short_flag:
        return ["-{}".format(short_flag), long_flag]
    return [long_flag]


def _add_step_argument(parser, short_flag, long_flag, help_template):
    """
    add a counting option to ``parser``, its help naming the flags bound
    """
    opts = _flag_option_strings(short_flag, long_flag)
    parser.add_argument(
        *opts,
        action="count",
        default=0,
        help=help_template.format(opt="/".join(opts)),
    )


def _add_extremity_argument(parser, short_flag, long_flag, dest, help_text):
    """
    add an option to ``parser`` that sets ``dest`` to the extreme
    """
    parser.add_argument(
        *_flag_option_strings(short_flag, long_flag),
        dest=dest,
        action="store_const",
        const=_EXTREME_VERBOSITY,
        default=0,
        help=help_text,
    )


def add_verbose_arguments(
    parser,
    *,
    step_flags="vq",
    extremity_flags="VQ",
):
    """
    add verbosity options to ``parser``, in two behaviors:

    - **step** — ``--verbose``/``--quiet``, each occurrence shifts
      verbosity up/down by one
    - **extremity** — ``--max-verbose``/``--max-quiet``, jumps
      straight to the maximum/minimum verbosity

    those four long options are always added. ``step_flags`` and
    ``extremity_flags`` only choose which single-letter short flag, if
    any, is bound alongside each behavior; each takes one of three
    values:

    - ``"vq"`` — bind ``-v`` and ``-q`` as the pair's short flags
    - ``"VQ"`` — bind ``-V`` and ``-Q`` as the pair's short flags
    - ``""`` — bind no short flag; the behavior stays reachable only
      through its long options

    eg the default ``step_flags="vq"``, ``extremity_flags="VQ"`` binds:

    - ``-v``/``-q`` alongside ``--verbose``/``--quiet``
    - ``-V``/``-Q`` alongside ``--max-verbose``/``--max-quiet``

    whereas ``step_flags="VQ"``, ``extremity_flags=""`` binds:

    - ``-V``/``-Q`` alongside ``--verbose``/``--quiet``
    - no short flag alongside ``--max-verbose``/``--max-quiet``


    :param parser: argument parser to extend
    :type parser: argparse.ArgumentParser
    :param step_flags: short-flag pair bound to the step behavior;
            one of ``"vq"``, ``"VQ"``, ``""``; default=``"vq"``
    :type step_flags: str, optional
    :param extremity_flags: short-flag pair bound to the extremity
            behavior; one of ``"vq"``, ``"VQ"``, ``""``;
            default=``"VQ"``
    :type extremity_flags: str, optional
    :raises ValueError: step_flags is not one of ``"vq"``, ``"VQ"``, ``""``
    :raises ValueError: extremity_flags is not one of ``"vq"``, ``"VQ"``,
            ``""``
    :raises ValueError: step_flags and extremity_flags are the same
            non-empty pair, which would bind one flag letter twice
    """
    for param, flags in (
        ("step_flags", step_flags),
        ("extremity_flags", extremity_flags),
    ):
        if flags not in _VERBOSE_FLAG_CHOICES:
            raise ValueError(
                "param {} {!r} must be one of {!r}".format(
                    param, flags, _VERBOSE_FLAG_CHOICES
                )
            )
    if step_flags and step_flags == extremity_flags:
        raise ValueError(
            "param step_flags and extremity_flags conflict: "
            "both are {!r}".format(step_flags)
        )

    v_flag, q_flag = step_flags or ("", "")
    ev_flag, eq_flag = extremity_flags or ("", "")

    _add_step_argument(parser, v_flag, "--verbose", _STEP_VERBOSE_HELP)
    _add_step_argument(parser, q_flag, "--quiet", _STEP_QUIET_HELP)
    _add_extremity_argument(
        parser, ev_flag, "--max-verbose", "verbose", _EXTREMITY_VERBOSE_HELP
    )
    _add_extremity_argument(
        parser, eq_flag, "--max-quiet", "quiet", _EXTREMITY_QUIET_HELP
    )


def calc_verbosity(namespace, *, verbosity=0):
    """
    apply namespace's verbose/quiet counts as an offset to verbosity


    :param namespace: parsed namespace containing ``--verbose`` and/or
            ``--quiet`` counts
    :type namespace: argparse.Namespace
    :param verbosity: base verbosity that namespace's ``--verbose``/``--quiet``
            counts are added to/subtracted from; default=0
    :type verbosity: int, optional
    :return: resulting verbosity after applying namespace's offset
    :rtype: int
    """
    if hasattr(namespace, "verbose"):
        verbosity += namespace.verbose
    if hasattr(namespace, "quiet"):
        verbosity -= namespace.quiet
    return verbosity


# verbosity → level; values beyond ±3 clamp to the ends
_VERBOSITY2LEVEL = {
    3: DEBUG,
    2: ENTER,
    1: INFO,
    0: DONE,
    -1: WARNING,
    -2: ERROR,
    -3: CRITICAL,
}


def calc_logging_level(verbosity, *, namespace=None):
    """
    map a verbosity integer to a logging level, optionally offset by
    namespace's verbose/quiet counts


    :param verbosity: base verbosity integer; higher is more verbose
    :type verbosity: int
    :param namespace: parsed namespace containing ``--verbose`` and/or
            ``--quiet`` counts, applied via :func:`calc_verbosity` to
            offset ``verbosity`` before mapping; default=None
    :type namespace: argparse.Namespace, optional
    :return: logging level corresponding to the resulting verbosity
    :rtype: int
    """
    if namespace is not None:
        verbosity = calc_verbosity(namespace, verbosity=verbosity)

    return _VERBOSITY2LEVEL[max(-3, min(3, verbosity))]


# set logger level  ------------------------------------------------------------


def set_logging_level_by_namespace(
    namespace, *, verbosity=0, logger=None, logger_name=None
):
    """
    set the logging level of a logger based on verbosity flags


    :param namespace: parsed namespace containing ``--verbose`` and/or
            ``--quiet`` counts
    :type namespace: argparse.Namespace
    :param verbosity: base verbosity that namespace's ``--verbose``/``--quiet``
            counts are added to/subtracted from; default=0
    :type verbosity: int, optional
    :param logger: logger instance to configure; default=None
    :type logger: logging.Logger, optional
    :param logger_name: name of logger to configure;
            ``None`` targets the root logger;
            ignored when ``logger`` is provided; default=None
    :type logger_name: str, optional
    """
    _set_logger_level(
        calc_logging_level(verbosity, namespace=namespace),
        logger=logger,
        logger_name=logger_name,
    )


def set_logging_level_by_verbosity(verbosity, *, logger=None, logger_name=None):
    """
    set the logging level of a logger based on a verbosity integer


    :param verbosity: verbosity integer; higher is more verbose
    :type verbosity: int
    :param logger: logger instance to configure; default=None
    :type logger: logging.Logger, optional
    :param logger_name: name of logger to configure;
            ``None`` targets the root logger;
            ignored when ``logger`` is provided; default=None
    :type logger_name: str, optional
    """
    _set_logger_level(
        calc_logging_level(verbosity),
        logger=logger,
        logger_name=logger_name,
    )


# Comment Banner  ##############################################################


_CONTENT_SPACING = "  "
_PADDING_MAP = {1: "#", 2: "=", 3: "*", 4: "+", 5: "-"}


def _resolve_padding_preset(padding):
    """
    :raises ValueError: ``padding`` is an int outside 1~5
    :return: padding char for preset ``padding`` (1~5); any other
            ``padding`` unchanged
    :rtype: str
    """
    if not isinstance(padding, int):
        return padding
    if padding not in _PADDING_MAP:
        raise ValueError("param padding int must be 1~5")
    return _PADDING_MAP[padding]


def _check_banner_content(content, line_width):
    """
    raise ``ValueError`` unless ``content`` is one line fitting ``line_width``
    """
    if "\n" in content:
        raise ValueError("param content must be a single line")
    if len(content) > line_width:
        raise ValueError(
            "param content length {} exceeds line_width {}".format(
                len(content), line_width
            )
        )


def _check_padding_char(padding):
    """
    raise ``ValueError`` unless ``padding`` is one printable non-space char
    """
    if len(padding) != 1:
        raise ValueError("param padding must be a single character")
    if not padding.isprintable() or padding == " ":
        raise ValueError("param padding must be a normal printable character")


def _grey_fill(renderer, padding, n):
    """
    :return: ``padding`` repeated ``n`` times, colored grey
    :rtype: str
    """
    return renderer.color_grey(padding * n)


def _resolve_renderer(renderer, file):
    """
    :return: ``renderer``, or a new one for ``file`` when ``None``
    :rtype: AnsiRenderer
    """
    return AnsiRenderer(file) if renderer is None else renderer


def _gen_comment_banner_generic(
    mode,
    content,
    padding,
    *,
    line_width=80,
    horizontal_offset=0,
    file=sys.stdout,
    renderer=None,
):
    """
    return ``content`` padded to ``line_width``, aligned per ``mode``:
    ``"c"`` centered, ``"l"`` left-justified, ``"r"`` right-justified
    """
    padding = _resolve_padding_preset(padding)
    _check_banner_content(content, line_width)
    _check_padding_char(padding)
    renderer = _resolve_renderer(renderer, file)

    if mode in ("l", "r"):
        remaining = line_width - len(content) - len(_CONTENT_SPACING)
        fill = _grey_fill(renderer, padding, remaining)
        if mode == "l":
            return content + _CONTENT_SPACING + fill
        return fill + _CONTENT_SPACING + content

    # centered; horizontal_offset shifts content: -1 left, +1 right
    remaining = line_width - len(content) - len(_CONTENT_SPACING) * 2
    left = remaining // 2 + horizontal_offset
    right = remaining - left
    if left < 0 or right < 0:
        raise ValueError("param horizontal_offset out of range")
    return (
        _grey_fill(renderer, padding, left)
        + _CONTENT_SPACING
        + content
        + _CONTENT_SPACING
        + _grey_fill(renderer, padding, right)
    )


# Comment Banner Public API  ===================================================


def gen_comment_banner_centered(*args, **kwargs):
    """
    generate a line with ``content`` centered,
    filling both sides with ``padding`` to reach ``line_width``

    when the remaining width is odd, the extra character goes to the right


    :param content: text to pad; must be a single, non-empty line no
            longer than ``line_width``
    :type content: str
    :param padding: single printable non-space fill character, or int 1-5
            (1: #, 2: =, 3: *, 4: +, 5: -)
    :type padding: str or int
    :param line_width: total output width; default=80
    :type line_width: int, optional
    :param horizontal_offset: nudge the centered content sideways by this
            many columns; negative shifts left, positive shifts right;
            default=0
    :type horizontal_offset: int, optional
    :param file: output stream, used only for ANSI TTY detection;
            default=``sys.stdout``
    :type file: IO, optional
    :param renderer: ANSI color renderer;
            if ``None``, created from ``file`` argument; default=None
    :type renderer: AnsiRenderer or None, optional
    :raises ValueError: ``content`` contains ``"\\n"`` or exceeds
            ``line_width``
    :raises ValueError: ``padding`` is not exactly one printable non-space
            character, or is an int outside 1-5
    :raises ValueError: ``horizontal_offset`` pushes either fill side below
            zero
    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_centered("hi", "=", line_width=20)
    '=======  hi  ======='
    >>> gen_comment_banner_centered(
    ...     "hi", "=", line_width=20, horizontal_offset=2
    ... )
    '=========  hi  ====='
    >>> gen_comment_banner_centered("hi", 2, line_width=20)
    '=======  hi  ======='
    """
    return _gen_comment_banner_generic("c", *args, **kwargs)


def gen_comment_banner_left_just(*args, **kwargs):
    """
    generate a line with ``content`` left-justified,
    filling the right with ``padding``

    see :func:`gen_comment_banner_centered` for parameter and error
    details


    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_left_just("hi", "=", line_width=20)
    'hi  ================'
    >>> gen_comment_banner_left_just("hi", 2, line_width=20)
    'hi  ================'
    """
    return _gen_comment_banner_generic("l", *args, **kwargs)


def gen_comment_banner_right_just(*args, **kwargs):
    """
    generate a line with ``content`` right-justified,
    filling the left with ``padding``

    see :func:`gen_comment_banner_centered` for parameter and error
    details


    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_right_just("hi", "=", line_width=20)
    '================  hi'
    >>> gen_comment_banner_right_just("hi", 2, line_width=20)
    '================  hi'
    """
    return _gen_comment_banner_generic("r", *args, **kwargs)


def gen_comment_banner_zero(
    lines, *, line_width=80, file=sys.stdout, renderer=None
):
    """
    generate a multi-line boxed comment banner (CB0)

    wraps each line with `# `, framed by top and bottom `#` rulers


    :param lines: lines to include in the banner
    :type lines: iterable of str
    :param line_width: total output width; default=80
    :type line_width: int, optional
    :param file: output stream, used only for ANSI TTY detection;
            default=``sys.stdout``
    :type file: IO, optional
    :param renderer: ANSI color renderer;
            if ``None``, created from ``file`` argument; default=None
    :type renderer: AnsiRenderer or None, optional
    :raises ValueError: any line contains ``"\\n"`` or exceeds
            ``line_width - 2`` (reserved for `# ` prefix)
    :return: multi-line boxed banner as a string
    :rtype: str
    :example:
    >>> gen_comment_banner_zero(["line 1", "line 2"], line_width=20)
    ####################
    # line 1
    # line 2
    ####################
    """
    renderer = _resolve_renderer(renderer, file)

    ruler = renderer.color_grey("#" * line_width)
    formatted_lines = [ruler]

    for line in lines:
        if "\n" in line:
            raise ValueError("param lines must not contain newlines")
        if len(line) > line_width - 2:
            raise ValueError(
                "param line length {} exceeds line_width - 2 {}".format(
                    len(line), line_width - 2
                )
            )
        formatted_lines.append(renderer.color_grey("# ") + line)

    formatted_lines.append(ruler)
    return "\n".join(formatted_lines)


# comment banner parser  =======================================================

_COMMENT_BANNER_HELP = "print stdin content padded to line width"


_COMMENT_BANNER_DESCRIPTION = _COMMENT_BANNER_HELP + """

content is read from stdin, as a single line

example:
  echo 'hello world' | kamilog cb c '=' -w 20"""


def _comment_banner_parser_main(args):
    mode_map = {"center": "c", "left": "l", "right": "r"}
    mode = mode_map.get(args.mode, args.mode)
    file = sys.stdout
    renderer = AnsiRenderer(file, is_disabled=args.no_color)
    raw, content = _read_stdin_line()
    padding = int(args.padding) if args.padding in "12345" else args.padding
    line = _gen_comment_banner_generic(
        mode,
        content,
        padding,
        line_width=args.line_width,
        file=file,
        renderer=renderer,
    )
    _print_output(args, line, raw)


def _register_comment_banner_parser(cli_subparser):
    """
    register the ``comment_banner`` subcommand on ``cli_subparser``
    """
    comment_banner_parser = _add_subcommand(
        cli_subparser,
        "comment_banner",
        "cb",
        [_line_width_parser],
        _COMMENT_BANNER_HELP,
        _COMMENT_BANNER_DESCRIPTION,
        _comment_banner_parser_main,
    )

    comment_banner_parser.add_argument(
        "mode",
        choices=["c", "l", "r", "center", "left", "right"],
        help=(
            "text alignment: c/center, l/left(-justified), r/right(-justified)"
        ),
    )
    comment_banner_parser.add_argument(
        "padding",
        metavar="PADDING",
        help="fill char, or int 1~5 for CB1~CB5 preset (1:#/2:=/3:*/4:+/5:-)",
    )


# cb0 parser  ==================================================================

_CB0_HELP = "print multi-line boxed comment banner (CB0)"


_CB0_DESCRIPTION = _CB0_HELP + """

lines are read from stdin, one banner line per stdin line

example:
  printf 'line 1\\nline 2\\n' | kamilog cb0 -w 20"""


def _comment_banner_zero_parser_main(args):
    file = sys.stdout
    renderer = AnsiRenderer(file, is_disabled=args.no_color)
    raw = sys.stdin.read()  # all lines from stdin
    lines = raw.splitlines()
    banner = gen_comment_banner_zero(
        lines,
        line_width=args.line_width,
        file=file,
        renderer=renderer,
    )
    _print_output(args, banner, raw)


def _register_comment_banner_zero_parser(cli_subparser):
    """
    register the ``comment_banner_zero`` subcommand on ``cli_subparser``
    """
    _add_subcommand(
        cli_subparser,
        "comment_banner_zero",
        "cb0",
        [_line_width_parser],
        _CB0_HELP,
        _CB0_DESCRIPTION,
        _comment_banner_zero_parser_main,
    )


# color parser  ================================================================

_COLOR_HELP = "print stdin content with ANSI style applied"

_COLOR_DESCRIPTION = _COLOR_HELP + """

content is read from stdin, as a single line

ANSI STYLE:

BOLD UNDERLINE

RED YELLOW GREEN CYAN BLUE MAGENTA
BRIGHT_RED BRIGHT_YELLOW ~~ (8 bright colors)
BLACK GREY WHITE BRIGHT_WHITE

BG_RED BG_BRIGHT_RED BG_BLACK (16 background colors)

example:
  echo 'hello world' | kamilog color RED BOLD"""


def _parse_ansi_style(raw):
    """
    argparse ``type`` adapter for ``AnsiStyle.parse``, mapping an unknown
    member name to ``ArgumentTypeError`` instead of ``ValueError``
    """
    try:
        return AnsiStyle.parse(raw)
    except ValueError as e:
        raise ArgumentTypeError(str(e)) from e


def _print_colored_stdin_line(args, style):
    """
    read a single stdin line, apply ``style``, and print the result,
    honoring ``-n/-N`` via ``args``
    """
    file = sys.stdout
    renderer = AnsiRenderer(file)
    raw, content = _read_stdin_line()
    _print_output(args, renderer.color(content, style), raw)


def _color_parser_main(args):
    style = AnsiStyle(0)
    for s in args.style:
        style |= s
    _print_colored_stdin_line(args, style)


def _register_color_parser(cli_subparser):
    """
    register the ``color`` subcommand on ``cli_subparser``
    """
    color_parser = _add_subcommand(
        cli_subparser,
        "color",
        "c",
        [_common_parser],
        _COLOR_HELP,
        _COLOR_DESCRIPTION,
        _color_parser_main,
    )

    color_parser.add_argument(
        "style",
        metavar="STYLE",
        nargs="+",
        type=_parse_ansi_style,
        help="1+ ANSI styles, v.s.",
    )


# color-grey parser  ===========================================================

_COLOR_GREY_HELP = "print stdin content in grey"

_COLOR_GREY_DESCRIPTION = _COLOR_GREY_HELP + """

equivalent to `color GREY`

content is read from stdin, as a single line

example:
  echo 'hello world' | kamilog color-grey"""


def _color_grey_parser_main(args):
    _print_colored_stdin_line(args, AnsiStyle.GREY)


def _register_color_grey_parser(cli_subparser):
    """
    register the ``color-grey`` subcommand on ``cli_subparser``
    """
    _add_subcommand(
        cli_subparser,
        "color-grey",
        "cg",
        [_common_parser],
        _COLOR_GREY_HELP,
        _COLOR_GREY_DESCRIPTION,
        _color_grey_parser_main,
    )


# deed CLI  ====================================================================
_DEED_HELP = "log one deed, e.g. a file copy, in its fixed wording"
_DEED_DESCRIPTION = _DEED_HELP + """
add '-- COMMAND' to run COMMAND and log its outcome instead: exit status 0
logs success, anything else logs failure, and the status is passed back
"""


def _run_deed_command(command, act):
    """
    run the wrapped `command`; mark `act` failed on a non-zero status
    and return the status as a shell would report it
    """
    try:
        status = subprocess.run(command, check=False).returncode
    except OSError as exc:
        act.fail("{}: {}".format(type(exc).__name__, exc))
        return 127 if isinstance(exc, FileNotFoundError) else 126
    if status < 0:  # killed by signal, as shells report it
        status = 128 - status
    if status:
        act.fail("exit {}".format(status))
    return status


def _deed_parser_main(args):
    deed = args.deed
    tail = args.tail_command
    deed_args = [getattr(args, name) for name in deed.arg_names]
    deed_args = [val for val in deed_args if val is not None]
    if tail is None:
        if args.err_level is not None:
            args.deed_parser.error("--err-level needs a command after '--'")
        if not deed_args:  # only run-command may omit its subject
            args.deed_parser.error(
                "the following arguments are required: {}".format(
                    deed.arg_names[0]
                )
            )
    elif deed.name == "run_command":
        if deed_args:
            args.deed_parser.error("the command is given after '--' only")
        deed_args = [shlex.join(tail)]

    logger = getLogger(disable_color=args.no_color)
    logger.setLevel(logging.DEBUG)  # --level alone decides what shows
    level = _resolve_level_name(args.level)
    err_level = _resolve_level_name(args.err_level)

    if tail is None:
        getattr(logger, deed.name)(*deed_args, level=level)
        return 0
    tracked = getattr(logger.track, deed.name)(
        *deed_args, level=level, err_level=err_level
    )
    with tracked as act:
        status = _run_deed_command(tail, act)
    return status


def _register_deed_parser(cli_subparser):
    """
    register the ``deed`` subcommand, with one sub-subcommand per deed
    """
    deed_parser = _add_subcommand(
        cli_subparser, "deed", None, [], _DEED_HELP, _DEED_DESCRIPTION, None
    )
    deed_parser.set_defaults(func=lambda _: deed_parser.print_help())
    deed_subparser = deed_parser.add_subparsers(title="deeds", metavar="DEED")

    for deed in _DEEDS.values():
        sub_parser = deed_subparser.add_parser(
            deed.name.replace("_", "-"),
            parents=[_no_color_parser],
            help=deed.template,
            description="log the deed ``{}``".format(deed.template),
        )
        for i, name in enumerate(deed.arg_names):
            # the subject is required, except that run-command may take its
            # command after '--'; trailing arguments may be omitted
            is_optional = i > 0 or deed.name == "run_command"
            sub_parser.add_argument(
                name, nargs="?" if is_optional else None, default=None
            )
        sub_parser.add_argument(
            "--level",
            choices=list(_LOGGER_LEVEL_MAP),
            default=None,
            help="level of the success line; default={}".format(
                logging.getLevelName(deed.level)
            ),
        )
        sub_parser.add_argument(
            "--err-level",
            choices=list(_LOGGER_LEVEL_MAP),
            default=None,
            help="level of the failure line, with '-- command'; default={}"
            .format(logging.getLevelName(deed.err_level)),
        )
        sub_parser.set_defaults(
            func=_deed_parser_main,
            deed=deed,
            deed_parser=sub_parser,
            tail_command=None,
        )


# CLI main parser  #############################################################

class _CliArgumentParser(ArgumentParser):
    """
    top-level parser that splits `deed ... -- COMMAND` at the first `--`
    """

    def parse_known_args(self, args=None, namespace=None):
        args = list(sys.argv[1:] if args is None else args)
        if args[:1] != ["deed"] or "--" not in args:
            return super().parse_known_args(args, namespace)
        idx = args.index("--")
        head, tail = args[:idx], args[idx + 1 :]
        if not tail:
            self.error("expected a command after '--'")
        namespace, extras = super().parse_known_args(head, namespace)
        namespace.tail_command = tail
        return namespace, extras


_cli_parser = _CliArgumentParser(
    prog="kamilog[.py]",
    description="kamilog CLI: utilities for formatted output and logging",
)
_cli_parser.set_defaults(func=lambda _: _cli_parser.print_help())
_cli_subparser = _cli_parser.add_subparsers(title="subcommands")


# register subcommands

_register_color_parser(_cli_subparser)
_register_color_grey_parser(_cli_subparser)
_register_comment_banner_parser(_cli_subparser)
_register_comment_banner_zero_parser(_cli_subparser)
_register_logger_parser(_cli_subparser)
_register_deed_parser(_cli_subparser)


# Entry Point  #################################################################


def kamilog_cli_main():
    """
    run the kamilog CLI, dispatching to the parsed subcommand's handler
    """
    parsed_args = _cli_parser.parse_args()
    status = parsed_args.func(parsed_args)
    if status:  # a wrapped command's exit status goes back to the shell
        sys.exit(status)


if __name__ == "__main__":
    kamilog_cli_main()
