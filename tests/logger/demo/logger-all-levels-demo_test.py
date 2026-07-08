"""
logger-all-levels-demo_test.py

tests for `KamiLogger`'s eleven log levels and their stdout/stderr
routing in `kamilog.py`
"""

import contextlib
import io
import logging

import pytest

import kamilog

_STDOUT_LEVEL_CASES = [
    ("debug", "Debugging details here", "DEBUG: Debugging details here"),
    ("info", "Informational message", "INFO : Informational message"),
    ("enter", "Starting database migration", "ENTER: Starting database migration"),
    ("skip", "Skipped validation step", "SKIP : Skipped validation step"),
    ("pass_", "All assertions passed", "PASS : All assertions passed"),
    ("succ", "User authentication succeeded", "SUCC.: User authentication succeeded"),
    ("done", "Migration completed successfully", "DONE : Migration completed successfully"),
]

_STDERR_LEVEL_CASES = [
    ("warning", "Warning message", "WARN.: Warning message"),
    ("error", "Error occurred", "ERROR: Error occurred"),
    ("critical", "Critical issue", "CRIT.: Critical issue"),
    ("fail", "Test case failed", "FAIL : Test case failed"),
]

_ALL_LEVELS_IN_ORDER_CALLS = [
    ("debug", "Debugging information shown only during development"),
    ("enter", "Marks start of a routine"),
    ("skip", "Marks skipped portion of routine"),
    ("succ", "Subroutine or execution succeeded"),
    ("info", "General informational message related to program function"),
    ("pass_", "Test case passed"),
    ("done", "Entire program or major component completed successfully"),
    ("warning", "Warning condition that should be investigated"),
    ("error", "Error condition that prevented operation completion"),
    ("fail", "Test case or subroutine/execution failed"),
    ("critical", "Program stopping or crashing immediately"),
]

_ALL_LEVELS_IN_ORDER_STDOUT = [
    "DEBUG: Debugging information shown only during development",
    "ENTER: Marks start of a routine",
    "SKIP : Marks skipped portion of routine",
    "SUCC.: Subroutine or execution succeeded",
    "INFO : General informational message related to program function",
    "PASS : Test case passed",
    "DONE : Entire program or major component completed successfully",
]

_ALL_LEVELS_IN_ORDER_STDERR = [
    "WARN.: Warning condition that should be investigated",
    "ERROR: Error condition that prevented operation completion",
    "FAIL : Test case or subroutine/execution failed",
    "CRIT.: Program stopping or crashing immediately",
]


def _fresh_root_logger():
    """
    reset then return the root logger, so a new handler binds to
    whichever stdout/stderr is active at call time
    """
    log = logging.getLogger()
    log.handlers = []
    log.filters = []
    log = kamilog.getLogger(datefmt=None)
    log.setLevel(kamilog.DEBUG)
    return log


def _run_and_capture(calls):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        log = _fresh_root_logger()
        for method, message in calls:
            getattr(log, method)(message)
    return out.getvalue(), err.getvalue()


class TestStandardAndCustomLevelsRouteToStdout:
    @pytest.mark.parametrize("method, message, expected", _STDOUT_LEVEL_CASES)
    def test_line(_, method, message, expected):
        out, err = _run_and_capture([(method, message)])
        assert out == expected + "\n"
        assert err == ""


class TestStandardAndCustomLevelsRouteToStderr:
    @pytest.mark.parametrize("method, message, expected", _STDERR_LEVEL_CASES)
    def test_line(_, method, message, expected):
        out, err = _run_and_capture([(method, message)])
        assert err == expected + "\n"
        assert out == ""


class TestAllLevelsInOrder:
    _out, _err = _run_and_capture(_ALL_LEVELS_IN_ORDER_CALLS)
    _out_lines = _out.splitlines()
    _err_lines = _err.splitlines()

    @pytest.mark.parametrize("i", range(len(_ALL_LEVELS_IN_ORDER_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestAllLevelsInOrder._out_lines[i]
            == _ALL_LEVELS_IN_ORDER_STDOUT[i]
        )

    @pytest.mark.parametrize("i", range(len(_ALL_LEVELS_IN_ORDER_STDERR)))
    def test_stderr_line(_, i):
        assert (
            TestAllLevelsInOrder._err_lines[i]
            == _ALL_LEVELS_IN_ORDER_STDERR[i]
        )
