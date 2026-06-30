"""
v-set_logging_level_by_verbosity_test.py

tests for `set_logging_level_by_verbosity` in `kamilog.py`
"""

import logging
from argparse import ArgumentParser
from kamilog.kamilog import add_verbose_arguments, set_logging_level_by_verbosity, SUCC, DONE

LOGGER_NAME = "TestSetLoggingLevelByVerbosity"


class TestSetLoggingLevelByVerbosity:
    def test_no_flags(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == DONE

    def test_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == logging.INFO

    def test_v2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == SUCC

    def test_v3(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vvv"])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == logging.DEBUG

    def test_q1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-q"])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == logging.WARNING

    def test_q2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-qq"])
        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        assert logging.getLogger(LOGGER_NAME).level == logging.ERROR
