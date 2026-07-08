"""
logger-handler-routing_test.py

tests for `getLogger` stdout/stderr handler routing in `kamilog.py`
"""

import logging
import sys
import uuid

from kamilog.kamilog import getLogger


def _make_record(levelno):
    return logging.LogRecord(
        "x", levelno, "path", 1, "message", (), None
    )


class TestHandlerCount:
    def test_two_handlers_are_attached(_):
        logger = getLogger(uuid.uuid4().hex)
        assert len(logger.handlers) == 2


class TestHandlerStreams:
    def test_first_handler_targets_stdout(_):
        logger = getLogger(uuid.uuid4().hex)
        assert logger.handlers[0].stream is sys.stdout

    def test_second_handler_targets_stderr(_):
        logger = getLogger(uuid.uuid4().hex)
        assert logger.handlers[1].stream is sys.stderr


class TestHandlerLevelFilters:
    def test_stdout_handler_accepts_below_warning(_):
        logger = getLogger(uuid.uuid4().hex)
        stdout_handler = logger.handlers[0]
        assert stdout_handler.filters[0](_make_record(logging.INFO)) is True

    def test_stdout_handler_rejects_warning_and_above(_):
        logger = getLogger(uuid.uuid4().hex)
        stdout_handler = logger.handlers[0]
        assert stdout_handler.filters[0](_make_record(logging.WARNING)) is False

    def test_stderr_handler_rejects_below_warning(_):
        logger = getLogger(uuid.uuid4().hex)
        stderr_handler = logger.handlers[1]
        assert stderr_handler.filters[0](_make_record(logging.INFO)) is False

    def test_stderr_handler_accepts_warning_and_above(_):
        logger = getLogger(uuid.uuid4().hex)
        stderr_handler = logger.handlers[1]
        assert stderr_handler.filters[0](_make_record(logging.WARNING)) is True

    def test_stderr_handler_accepts_error(_):
        logger = getLogger(uuid.uuid4().hex)
        stderr_handler = logger.handlers[1]
        assert stderr_handler.filters[0](_make_record(logging.ERROR)) is True
