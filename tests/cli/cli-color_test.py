"""
cli-color_test.py

tests for the `color` CLI subcommand (alias `c`) in `kamilog`: `STYLE`
parsing via `_parse_ansi_style`, and its interaction with the shared
`-n`/`-N` flags from `_common_parser`; `color` does not inherit `-C`, since
disabling color makes no sense for a subcommand whose purpose is color
"""

import io

import pytest
from kamilog import AnsiRenderer, AnsiStyle
from kamilog.cli import _cli_parser


class _FakeTtyStream(io.StringIO):
    def isatty(_):
        return True


def _run(argv, stdin_text, stream=None):
    stream = io.StringIO() if stream is None else stream
    args = _cli_parser.parse_args(argv)
    import sys as _sys

    old_stdin, old_stdout = _sys.stdin, _sys.stdout
    _sys.stdin, _sys.stdout = io.StringIO(stdin_text), stream
    try:
        args.func(args)
    finally:
        _sys.stdin, _sys.stdout = old_stdin, old_stdout
    return stream.getvalue()


class TestStyleArgumentParses:
    def test_single_style_name_parses(_):
        args = _cli_parser.parse_args(["color", "RED"])
        assert args.style == [AnsiStyle.RED]

    def test_multiple_style_names_are_ored_together(_):
        args = _cli_parser.parse_args(["color", "RED", "BOLD"])
        assert args.style == [AnsiStyle.RED, AnsiStyle.BOLD]

    def test_style_name_is_case_insensitive(_):
        args = _cli_parser.parse_args(["color", "red", "bold"])
        assert args.style == [AnsiStyle.RED, AnsiStyle.BOLD]

    def test_style_name_tolerates_surrounding_whitespace(_):
        args = _cli_parser.parse_args(["color", " RED "])
        assert args.style == [AnsiStyle.RED]

    def test_unknown_style_name_raises(_):
        with pytest.raises(SystemExit):
            _cli_parser.parse_args(["color", "NOTASTYLE"])

    def test_alias_parses_identically_to_full_name(_):
        args = _cli_parser.parse_args(["c", "RED"])
        assert args.style == [AnsiStyle.RED]


class TestColorHasNoDisableFlag:
    def test_default_colors_a_tty_stream(_):
        out = _run(["color", "RED"], "hi\n", stream=_FakeTtyStream())
        assert "\033[" in out

    def test_non_tty_stream_prints_plain_text(_):
        out = _run(["color", "RED"], "hi\n")
        assert out == "hi\n"

    def test_no_color_flag_is_rejected(_):
        with pytest.raises(SystemExit):
            _cli_parser.parse_args(["color", "RED", "-C"])


class TestMultipleStyleArgsCombineOnRender:
    def test_multiple_styles_are_ored_before_rendering(_):
        out = _run(["color", "RED", "BOLD"], "hi\n", stream=_FakeTtyStream())
        assert out == AnsiRenderer(_FakeTtyStream()).color(
            "hi", AnsiStyle.RED | AnsiStyle.BOLD
        ) + "\n"  # auto mode ends the line


class TestColorNewline:
    def test_auto_ends_in_one_newline_when_stdin_has_one(_):
        out = _run(["color", "RED"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_auto_ends_in_one_newline_when_stdin_has_none(_):
        out = _run(["color", "RED"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_newline_flag_appends_onto_stdin_newline(_):
        out = _run(["color", "RED", "-n"], "hi\n")
        assert out.endswith("\n\n")  # own break kept, one appended

    def test_newline_flag_appends_when_stdin_has_none(_):
        out = _run(["color", "RED", "-n"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_keeps_stdin_newline(_):
        out = _run(["color", "RED", "-N"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_appends_none_when_stdin_has_none(_):
        out = _run(["color", "RED", "-N"], "hi")
        assert not out.endswith("\n")
