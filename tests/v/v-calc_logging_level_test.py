"""
v-calc_logging_level_test.py

tests for `calc_logging_level` in `kamilog.py`
"""

import logging
from kamilog.kamilog import calc_logging_level, ENTER, DONE


class TestCalcLoggingLevel:
    def test_zero(_):
        assert calc_logging_level(0) == DONE

    def test_v1(_):
        assert calc_logging_level(1) == logging.INFO

    def test_v2(_):
        assert calc_logging_level(2) == ENTER

    def test_v3(_):
        assert calc_logging_level(3) == logging.DEBUG

    def test_v_over(_):
        assert calc_logging_level(99) == logging.DEBUG

    def test_q1(_):
        assert calc_logging_level(-1) == logging.WARNING

    def test_q2(_):
        assert calc_logging_level(-2) == logging.ERROR

    def test_q3(_):
        assert calc_logging_level(-3) == logging.CRITICAL
