"""
verbosity: ``-v``/``-q`` argument helpers and verbosity-to-level mapping
"""

import logging

from .levels import CRITICAL, DEBUG, DONE, ENTER, ERROR, INFO, WARNING


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
