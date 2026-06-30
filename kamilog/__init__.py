"""
kamilog: Customized Logging Output Module
"""

# HACK better auto import


from .kamilog import (
    KamiLogger,
    NOTSET,
    DEBUG,
    ENTER,
    SKIP,
    INFO,
    PASS,
    SUCC,
    DONE,
    WARNING,
    ERROR,
    FAIL,
    CRITICAL,
    DATEFMT_TIME,
    DATEFMT_TIME_MS,
    DATEFMT_DATETIME,
    DATEFMT_DATETIME_MS,
    getLogger,
    add_verbose_arguments,
    set_logging_level_by_verbosity,
    print_line_padding_centered,
    print_line_padding_left_just,
    print_line_padding_right_just,
)

__all__ = (
    "KamiLogger",
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
    "DATEFMT_TIME",
    "DATEFMT_TIME_MS",
    "DATEFMT_DATETIME",
    "DATEFMT_DATETIME_MS",
    "getLogger",
    "add_verbose_arguments",
    "set_logging_level_by_verbosity",
    "print_line_padding_centered",
    "print_line_padding_left_just",
    "print_line_padding_right_just",
)
