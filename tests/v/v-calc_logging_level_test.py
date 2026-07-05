"""
v-calc_logging_level_test.py

tests for `_calc_logging_level_from_verbosity` in `kamilog.py`
"""

import logging
from kamilog.kamilog import _calc_logging_level_from_verbosity, ENTER, DONE


class TestCalcLoggingLevel:
    def test_zero(_):
        assert _calc_logging_level_from_verbosity(0) == DONE

    def test_v1(_):
        assert _calc_logging_level_from_verbosity(1) == logging.INFO

    def test_v2(_):
        assert _calc_logging_level_from_verbosity(2) == ENTER

    def test_v3(_):
        assert _calc_logging_level_from_verbosity(3) == logging.DEBUG

    def test_v_over(_):
        assert _calc_logging_level_from_verbosity(99) == logging.DEBUG

    def test_q1(_):
        assert _calc_logging_level_from_verbosity(-1) == logging.WARNING

    def test_q2(_):
        assert _calc_logging_level_from_verbosity(-2) == logging.ERROR

    def test_q3(_):
        assert _calc_logging_level_from_verbosity(-3) == logging.CRITICAL
