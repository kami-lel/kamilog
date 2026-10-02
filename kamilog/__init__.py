"""
kamilog: Customized Logging Output Module
"""

from .ansi import AnsiRenderer, AnsiStyle
from .banner import (
    gen_comment_banner_centered,
    gen_comment_banner_left_just,
    gen_comment_banner_right_just,
    gen_comment_banner_zero,
)
from .cli import kamilog_cli_main
from .formatter import (
    DATEFMT_DATETIME,
    DATEFMT_DATETIME_MS,
    DATEFMT_TIME,
    DATEFMT_TIME_MS,
)
from .levels import (
    CAUTION,
    CRITICAL,
    DEBUG,
    DONE,
    ENTER,
    ERROR,
    FAIL,
    HINT,
    IMPORTANT,
    INFO,
    NOTE,
    NOTSET,
    PASS,
    SKIP,
    SUCC,
    TIP,
    WARNING,
)
from .logger import KamiLogger, getLogger
from .verbosity import (
    add_verbose_arguments,
    calc_logging_level,
    calc_verbosity,
    set_logging_level_by_namespace,
    set_logging_level_by_verbosity,
)

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
