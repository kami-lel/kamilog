"""
logger-custom-levels_test.py

tests for `KamiLogger` custom level methods in `kamilog.py`
"""

import logging
import uuid

from kamilog.kamilog import _CustomLogLevel


def _fresh_logger():
    return logging.getLogger(uuid.uuid4().hex)


class TestCustomLevelValues:
    def test_enter_is_fifteen(_):
        assert int(_CustomLogLevel.ENTER) == 15

    def test_skip_is_sixteen(_):
        assert int(_CustomLogLevel.SKIP) == 16

    def test_succ_is_seventeen(_):
        assert int(_CustomLogLevel.SUCC) == 17

    def test_pass_is_twenty_one(_):
        assert int(_CustomLogLevel.PASS) == 21

    def test_done_is_twenty_five(_):
        assert int(_CustomLogLevel.DONE) == 25

    def test_fail_is_forty_five(_):
        assert int(_CustomLogLevel.FAIL) == 45


class TestCustomLevelDisplayPadding:
    def test_every_display_is_five_chars(_):
        for lvl in _CustomLogLevel:
            assert len(lvl.display) == 5

    def test_succ_display_uses_dot_padding(_):
        assert _CustomLogLevel.SUCC.display == "SUCC."

    def test_enter_display_has_no_padding_needed(_):
        assert _CustomLogLevel.ENTER.display == "ENTER"


class TestLoggerIsKamiLoggerInstance:
    def test_newly_created_logger_has_custom_methods(_):
        logger = _fresh_logger()
        for method in ("enter", "skip", "succ", "pass_", "done", "fail"):
            assert hasattr(logger, method)


class TestCustomLevelEmission:
    def test_enter_emits_at_enter_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.ENTER, logger=logger.name)
        logger.enter("entering step")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == _CustomLogLevel.ENTER
        assert caplog.records[0].getMessage() == "entering step"

    def test_skip_emits_at_skip_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.SKIP, logger=logger.name)
        logger.skip("skipping step")
        assert caplog.records[0].levelno == _CustomLogLevel.SKIP

    def test_succ_emits_at_succ_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.SUCC, logger=logger.name)
        logger.succ("succeeded")
        assert caplog.records[0].levelno == _CustomLogLevel.SUCC

    def test_pass_emits_at_pass_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.PASS, logger=logger.name)
        logger.pass_("passed")
        assert caplog.records[0].levelno == _CustomLogLevel.PASS

    def test_done_emits_at_done_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.DONE, logger=logger.name)
        logger.done("done")
        assert caplog.records[0].levelno == _CustomLogLevel.DONE

    def test_fail_emits_at_fail_level(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.FAIL, logger=logger.name)
        logger.fail("failed")
        assert caplog.records[0].levelno == _CustomLogLevel.FAIL

    def test_args_are_interpolated(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.ENTER, logger=logger.name)
        logger.enter("hello %s", "world")
        assert caplog.records[0].getMessage() == "hello world"


class TestCustomLevelGating:
    def test_level_below_threshold_is_suppressed(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.SKIP, logger=logger.name)
        logger.enter("should not appear")
        assert len(caplog.records) == 0

    def test_level_at_threshold_is_emitted(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.SKIP, logger=logger.name)
        logger.skip("should appear")
        assert len(caplog.records) == 1

    def test_level_above_threshold_is_emitted(_, caplog):
        logger = _fresh_logger()
        caplog.set_level(_CustomLogLevel.SKIP, logger=logger.name)
        logger.succ("should appear too")
        assert len(caplog.records) == 1
