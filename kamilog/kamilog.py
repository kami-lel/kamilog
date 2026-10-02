"""
kamilog.py

Lightweight Python logging wrapper with custom log levels, structured output,
ANSI colored logging, verbosity control, comment banner utilities, and CLI.

Q.v. https://github.com/kami-lel/kamilog for Project Main Page
Q.v. https://github.com/kami-lel/kamilog/tree/main/docs for Documentation
"""

import logging
import shlex
import subprocess
import sys

from .ansi import AnsiRenderer, AnsiStyle
from .badges import _NATIVE_BADGES, _normalize_badges
from .banner import (
    _gen_comment_banner_generic, gen_comment_banner_centered,
    gen_comment_banner_left_just, gen_comment_banner_right_just,
    gen_comment_banner_zero,
)
from .deeds import (
    _DEEDS, _Deed, _DeedHandle, _DeedScope, _DeedTrack, _bind_deed_methods,
    _make_deed_method, _make_track_method, _raise_unexpected_deed_arg,
    _render_deed_message, _stringify_deed_args,
)
from .diff_only import _DiffOnlyEngine, _DiffOnlyMsgFilter
from .formatter import (
    DATEFMT_DATETIME, DATEFMT_DATETIME_MS, DATEFMT_TIME, DATEFMT_TIME_MS,
    _DATEFMT_AUTO, _PADDED_LEVELNAME_MAP, _LogFormatEngine, _LogFormatter,
)
from .levels import (
    CAUTION, CRITICAL, DEBUG, DONE, ENTER, ERROR, FAIL, HINT, IMPORTANT,
    INFO, NOTE, NOTSET, PASS, SKIP, SUCC, TIP, WARNING, _CustomLogLevel,
)
from .logger import (
    KamiLogger, _attach_console_handlers, _attach_diff_only_filter,
    _attach_file_handler, _build_console_handler, getLogger,
)
from .verbosity import (
    add_verbose_arguments, calc_logging_level, calc_verbosity,
    set_logging_level_by_namespace, set_logging_level_by_verbosity,
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
from .cli import _cli_parser, kamilog_cli_main

