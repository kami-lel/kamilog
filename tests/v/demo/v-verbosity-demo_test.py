"""
v-verbosity-demo_test.py

golden-output test for `examples/verbosity_demo.py`, covering
`add_verbose_arguments` and `set_logging_level_by_namespace` driving
`KamiLogger`'s eleven log levels in `kamilog.py`
"""

import argparse
import contextlib
import io
import logging

import pytest

import kamilog


_LABELS = {
    "debug": "DEBUG",
    "enter": "ENTER",
    "skip": "SKIP ",
    "succ": "SUCC.",
    "info": "INFO ",
    "pass_": "PASS ",
    "done": "DONE ",
    "warning": "WARN.",
    "error": "ERROR",
    "fail": "FAIL ",
    "critical": "CRIT.",
}

_STDERR_METHODS = {"warning", "error", "fail", "critical"}

_CALLS = [
    ("debug", "debug detail (visible with -vvv)", kamilog.DEBUG),
    ("enter", "entering subroutine (visible with -vv)", kamilog.ENTER),
    ("skip", "skipped step (visible with -vv)", kamilog.SKIP),
    ("succ", "operation succeeded (visible with -vv)", kamilog.SUCC),
    ("info", "info message (visible with -v)", kamilog.INFO),
    ("pass_", "test passed (visible with -v)", kamilog.PASS),
    ("done", "task completed (visible by default)", kamilog.DONE),
    ("warning", "warning (visible with -q or less)", kamilog.WARNING),
    ("error", "error (visible with -qq or less)", kamilog.ERROR),
    ("fail", "test failed (visible with -qq or less)", kamilog.FAIL),
    ("critical", "critical (visible with -qqq or less)", kamilog.CRITICAL),
]

_FLAG_CASES = [
    ([], kamilog.DONE),
    (["-v"], kamilog.INFO),
    (["-vv"], kamilog.ENTER),
    (["-vvv"], kamilog.DEBUG),
    (["-q"], kamilog.WARNING),
    (["-qq"], kamilog.ERROR),
    (["-qqq"], kamilog.CRITICAL),
]


def _fresh_root_logger():
    log = logging.getLogger()
    log.handlers = []
    log.filters = []
    return kamilog.getLogger()


def _run_demo(argv):
    parser = argparse.ArgumentParser(description="verbosity demo")
    kamilog.add_verbose_arguments(parser)
    args = parser.parse_args(argv)

    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        log = _fresh_root_logger()
        kamilog.set_logging_level_by_namespace(args)
        for method, message, _levelno in _CALLS:
            getattr(log, method)(message)
    return out.getvalue(), err.getvalue()


def _expected_lines(threshold):
    stdout_lines, stderr_lines = [], []
    for method, message, levelno in _CALLS:
        if levelno < threshold:
            continue
        line = "{}: {}".format(_LABELS[method], message)
        if method in _STDERR_METHODS:
            stderr_lines.append(line)
        else:
            stdout_lines.append(line)
    return stdout_lines, stderr_lines


class TestVerbosityDemoOutput:
    @pytest.mark.parametrize("argv, threshold", _FLAG_CASES)
    def test_flag_combination(_, argv, threshold):
        out, err = _run_demo(argv)
        expected_out, expected_err = _expected_lines(threshold)
        assert out.splitlines() == expected_out
        assert err.splitlines() == expected_err
