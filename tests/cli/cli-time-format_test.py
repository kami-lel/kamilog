"""
cli-time-format_test.py

tests for the `logger` CLI subcommand's `-t/--time-format` default & choices
in `kamilog`
"""

import io
import re
import sys
import uuid

import pytest

from kamilog.cli import _cli_parser


@pytest.fixture(autouse=True)
def _isolate_root_logger():
    """restore the root logger so other tests are unaffected"""
    import logging

    root = logging.getLogger()
    handlers, filters = root.handlers[:], root.filters[:]
    yield
    root.handlers[:], root.filters[:] = handlers, filters


def _run(argv, stdin_text):
    args = _cli_parser.parse_args(argv)
    old_stdin, old_stdout = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = io.StringIO(stdin_text), io.StringIO()
    try:
        args.func(args)
        return sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout


class TestTimeFormatDefault:
    def test_default_prints_no_timestamp(_):
        out = _run(["logger", "info", uuid.uuid4().hex], "hello\n")
        assert re.fullmatch(r"INFO  \S+: hello\n", out)

    def test_time_choice_prints_hh_mm_ss(_):
        out = _run(["logger", "info", "-t", "time", uuid.uuid4().hex], "hi\n")
        assert re.match(r"\d\d:\d\d:\d\d INFO  ", out)
