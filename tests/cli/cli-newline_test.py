"""
cli-newline_test.py

tests for the shared `-n/--newline`/`-N/--no-newline` flag's effect on the
`cb`, `cb0`, and `logger` CLI subcommands' printed output in `kamilog`
"""

import io
import uuid

from kamilog.cli import _cli_parser


def _run(argv, stdin_text):
    stdout = io.StringIO()
    args = _cli_parser.parse_args(argv)
    import sys as _sys

    old_stdin, old_stdout = _sys.stdin, _sys.stdout
    _sys.stdin, _sys.stdout = io.StringIO(stdin_text), stdout
    try:
        args.func(args)
    finally:
        _sys.stdin, _sys.stdout = old_stdin, old_stdout
    return stdout.getvalue()


class TestCommentBannerNewline:
    def test_auto_ends_in_one_newline_when_stdin_has_one(_):
        out = _run(["cb", "c", "=", "-w", "20"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_auto_ends_in_one_newline_when_stdin_has_none(_):
        out = _run(["cb", "c", "=", "-w", "20"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_newline_flag_appends_onto_stdin_newline(_):
        out = _run(["cb", "c", "=", "-w", "20", "-n"], "hi\n")
        assert out.endswith("\n\n")  # own break kept, one appended

    def test_newline_flag_appends_when_stdin_has_none(_):
        out = _run(["cb", "c", "=", "-w", "20", "-n"], "hi")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_keeps_stdin_newline(_):
        out = _run(["cb", "c", "=", "-w", "20", "-N"], "hi\n")
        assert out.endswith("\n") and not out.endswith("\n\n")

    def test_no_newline_flag_appends_none_when_stdin_has_none(_):
        out = _run(["cb", "c", "=", "-w", "20", "-N"], "hi")
        assert not out.endswith("\n")


# 4 banner lines, joined by 3 internal breaks the flags never touch
_CB0_INTERNAL_BREAKS = 3


class TestCommentBannerZeroNewline:
    def test_auto_ends_in_one_newline_when_stdin_has_one(_):
        out = _run(["cb0", "-w", "20"], "line 1\nline 2\n")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _CB0_INTERNAL_BREAKS + 1

    def test_auto_ends_in_one_newline_when_stdin_has_none(_):
        out = _run(["cb0", "-w", "20"], "line 1\nline 2")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _CB0_INTERNAL_BREAKS + 1

    def test_newline_flag_appends_onto_stdin_newline(_):
        out = _run(["cb0", "-w", "20", "-n"], "line 1\nline 2\n")
        assert out.endswith("\n\n")  # own break kept, one appended
        assert out.count("\n") == _CB0_INTERNAL_BREAKS + 2

    def test_newline_flag_appends_when_stdin_has_none(_):
        out = _run(["cb0", "-w", "20", "-n"], "line 1\nline 2")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _CB0_INTERNAL_BREAKS + 1

    def test_no_newline_flag_keeps_stdin_newline(_):
        out = _run(["cb0", "-w", "20", "-N"], "line 1\nline 2\n")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _CB0_INTERNAL_BREAKS + 1

    def test_no_newline_flag_appends_none_when_stdin_has_none(_):
        out = _run(["cb0", "-w", "20", "-N"], "line 1\nline 2")
        assert not out.endswith("\n")
        assert out.count("\n") == _CB0_INTERNAL_BREAKS


# 2 records, joined by 1 internal break the flags never touch
_LOGGER_INTERNAL_BREAKS = 1


class TestLoggerNewline:
    def test_auto_ends_in_one_newline_when_stdin_has_one(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name], "a\nb\n")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS + 1

    def test_auto_ends_in_one_newline_when_stdin_has_none(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name], "a\nb")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS + 1

    def test_newline_flag_appends_onto_stdin_newline(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name, "-n"], "a\nb\n")
        assert out.endswith("\n\n")  # own break kept, one appended
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS + 2

    def test_newline_flag_appends_when_stdin_has_none(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name, "-n"], "a\nb")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS + 1

    def test_no_newline_flag_keeps_stdin_newline(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name, "-N"], "a\nb\n")
        assert out.endswith("\n") and not out.endswith("\n\n")
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS + 1

    def test_no_newline_flag_appends_none_when_stdin_has_none(_):
        name = uuid.uuid4().hex
        out = _run(["logger", "info", name, "-N"], "a\nb")
        assert not out.endswith("\n")
        assert out.count("\n") == _LOGGER_INTERNAL_BREAKS
