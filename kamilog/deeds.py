"""
deeds: fixed-wording log methods for common acts, in plain and track form
"""

import logging
from collections import namedtuple
from string import Formatter as _TemplateParser

from .levels import ERROR, INFO, SKIP, WARNING


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
