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
import shlex
import subprocess
import sys

from .ansi import AnsiRenderer, AnsiStyle
from .badges import _NATIVE_BADGES, _normalize_badges
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
