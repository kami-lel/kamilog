from .kamilog import (
    KamiLogger,
    NOTSET,
    DEBUG,
    ENTER,
    SKIP,
    INFO,
    PASS,
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
    calc_verbosity,
    set_logging_level_by_verbosity,
)
from .kamilog import __doc__ as kamilog_doc

__all__ = (
    "KamiLogger",
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
    "DATEFMT_TIME",
    "DATEFMT_TIME_MS",
    "DATEFMT_DATETIME",
    "DATEFMT_DATETIME_MS",
    "getLogger",
    "add_verbose_arguments",
    "calc_verbosity",
    "set_logging_level_by_verbosity",
)

try:
    from importlib.metadata import version as _pkg_version, metadata as _pkg_meta, PackageNotFoundError
    __version__ = _pkg_version("kamilog")
    __author__ = _pkg_meta("kamilog")["Author"]
except PackageNotFoundError:
    __version__ = "unknown"
    __author__ = "unknown"

__doc__ = kamilog_doc
