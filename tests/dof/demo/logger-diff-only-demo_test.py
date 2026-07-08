"""
logger-diff-only-demo_test.py

tests for `_DiffOnlyMsgFilter` compressing repeated characters across
recent log history in `kamilog.py`
"""

import contextlib
import io
import re

import pytest

import kamilog

_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


def _run_and_capture(name, calls):
    """
    log ``calls`` (method, message) pairs through a fresh, non-propagating
    logger and return masked (stdout, stderr) text
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        log = kamilog.getLogger(name)
        log.setLevel(kamilog.DEBUG)
        log.propagate = False
        for method, message in calls:
            getattr(log, method)(message)
    return _mask_time(out.getvalue()), _mask_time(err.getvalue())


_BASIC_COMPRESSION_CALLS = [
    ("info", "sensor=cpu  load=45.2%  temp=61C  ok"),
    ("info", "sensor=cpu  load=47.8%  temp=62C  ok"),
    ("info", "sensor=cpu  load=44.1%  temp=60C  ok"),
    ("info", "sensor=cpu  load=51.3%  temp=63C  ok"),
    ("info", "sensor=cpu  load=49.7%  temp=62C  ok"),
    ("info", "sensor=cpu  load=53.0%  temp=64C  ok"),
]

_BASIC_COMPRESSION_STDOUT = [
    "<TIME> INFO  logger-diff-only-demo-sensor: sensor=cpu  load=45.2%  temp=61C  ok",
    "<TIME> INFO  logger-diff-only-demo-sensor: sensor=cpu  load=47.8%  temp=62C  ok",
    "<TIME> INFO  logger-diff-only-demo-sensor: sensor=cpu  load=44.1%  temp=60C  ok",
    "<TIME> INFO  logger-diff-only-demo-sensor: \t〃\t〃   =51.3%  temp=63C  ok",
    "<TIME> INFO  logger-diff-only-demo-sensor: \t〃\t〃   =49.7%  temp=62C  ok",
    "<TIME> INFO  logger-diff-only-demo-sensor: \t〃\t〃   =53.0%  temp=64C  ok",
]

_PATTERN_BREAK_CALLS = (
    [
        ("info", "sync /home/alice/docs/q{}_report.pdf  →  remote:backup  ok".format(i))
        for i in range(1, 6)
    ]
    + [("warning", "WARN disk 91 full on remote:backup — sync paused")]
    + [
        ("info", "sync /home/alice/docs/q{}_report.pdf  →  remote:backup  ok".format(i))
        for i in range(6, 10)
    ]
)

_PATTERN_BREAK_STDOUT = [
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q1_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q2_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q3_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: 〃\t〃\t〃\t/q4〃\t〃\t〃\t〃\t  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: 〃\t〃\t〃\t/q5〃\t〃\t〃\t〃\t  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q6_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q7_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: sync /home/alice/docs/q8_report.pdf  →  remote:backup  ok",
    "<TIME> INFO  logger-diff-only-demo-sync: 〃\t〃\t〃\t/q9〃\t〃\t〃\t〃\t  ok",
]

_PATTERN_BREAK_STDERR = [
    "<TIME> WARN. logger-diff-only-demo-sync: WARN disk 91 full on remote:backup — sync paused",
]


class TestBasicCompression:
    _out, _err = _run_and_capture(
        "logger-diff-only-demo-sensor", _BASIC_COMPRESSION_CALLS
    )
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestBasicCompression._err == ""

    @pytest.mark.parametrize("i", range(len(_BASIC_COMPRESSION_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestBasicCompression._out_lines[i]
            == _BASIC_COMPRESSION_STDOUT[i]
        )


class TestPatternBreakAndRecoveryWithOutlier:
    _out, _err = _run_and_capture(
        "logger-diff-only-demo-sync", _PATTERN_BREAK_CALLS
    )
    _out_lines = _out.splitlines()
    _err_lines = _err.splitlines()

    @pytest.mark.parametrize("i", range(len(_PATTERN_BREAK_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestPatternBreakAndRecoveryWithOutlier._out_lines[i]
            == _PATTERN_BREAK_STDOUT[i]
        )

    @pytest.mark.parametrize("i", range(len(_PATTERN_BREAK_STDERR)))
    def test_stderr_line(_, i):
        assert (
            TestPatternBreakAndRecoveryWithOutlier._err_lines[i]
            == _PATTERN_BREAK_STDERR[i]
        )
