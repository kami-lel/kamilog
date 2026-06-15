from .kamilog import (
    getLogger,
    add_verbose_arguments,
    calc_verbosity,
    set_logging_level_by_verbosity,
)
from .kamilog import __version__ as kamilog_version
from .kamilog import __author__ as kamilog_author
from .kamilog import __doc__ as kamilog_doc

__all__ = (
    "getLogger",
    "add_verbose_arguments",
    "calc_verbosity",
    "set_logging_level_by_verbosity",
)


__version__ = kamilog_version
__author__ = kamilog_author
__doc__ = kamilog_doc
