"""
command-line interface: the ``kamilog`` console script and its subcommands
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
from .banner import _gen_comment_banner_generic, gen_comment_banner_zero
from .deeds import _DEEDS
from .formatter import (
    DATEFMT_DATETIME, DATEFMT_DATETIME_MS, DATEFMT_TIME, DATEFMT_TIME_MS,
)
from .levels import CRITICAL, DEBUG, ERROR, INFO, WARNING, _CustomLogLevel
from .logger import getLogger
from .verbosity import add_verbose_arguments, set_logging_level_by_namespace


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
    prog="kamilog",
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
