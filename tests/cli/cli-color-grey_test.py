"""
cli-color-grey_test.py

tests for the `color-grey` CLI subcommand (alias `cg`) in `kamilog`:
equivalence to `color GREY`, and its interaction with the shared `-n`/`-N`
flags from `_common_parser`; `color-grey` does not inherit `-C`, same as
`color`
"""

import io

import pytest
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


class TestColorGreyMatchesColorGrey:
    def test_output_matches_color_grey_on_tty_stream(_):
        grey_out = _run(["color-grey"], "hi\n", stream=_FakeTtyStream())
        color_out = _run(["color", "GREY"], "hi\n", stream=_FakeTtyStream())
        assert grey_out == color_out

    def test_output_matches_color_grey_on_non_tty_stream(_):
        grey_out = _run(["color-grey"], "hi\n")
        color_out = _run(["color", "GREY"], "hi\n")
        assert grey_out == color_out

    def test_alias_parses_identically_to_full_name(_):
        grey_out = _run(["cg"], "hi\n", stream=_FakeTtyStream())
        color_out = _run(["color", "GREY"], "hi\n", stream=_FakeTtyStream())
        assert grey_out == color_out

    def test_takes_no_style_argument(_):
        with pytest.raises(SystemExit):
            _cli_parser.parse_args(["color-grey", "RED"])


class TestColorGreyHasNoDisableFlag:
    def test_no_color_flag_is_rejected(_):
        with pytest.raises(SystemExit):
            _cli_parser.parse_args(["color-grey", "-C"])


class TestColorGreyNewline:
    def test_auto_ends_in_one_newline_when_stdin_has_one(_):
        out = _run(["color-grey"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_auto_ends_in_one_newline_when_stdin_has_none(_):
        out = _run(["color-grey"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_newline_flag_appends_onto_stdin_newline(_):
        out = _run(["color-grey", "-n"], "hi\n")
        assert out.endswith("\n\n")  # own break kept, one appended

    def test_newline_flag_appends_when_stdin_has_none(_):
        out = _run(["color-grey", "-n"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_keeps_stdin_newline(_):
        out = _run(["color-grey", "-N"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_appends_none_when_stdin_has_none(_):
        out = _run(["color-grey", "-N"], "hi")
        assert not out.endswith("\n")
