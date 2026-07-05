"""
v-calc_logging_level_namespace_test.py

tests for `_calc_logging_level_from_verbosity_namespace` in `kamilog.py`
"""

import logging
from argparse import ArgumentParser
from kamilog.kamilog import (
    add_verbose_arguments,
    _calc_logging_level_from_verbosity_namespace,
    ENTER,
    DONE,
)


class TestCalcLoggingLevelNamespace:
    def test_no_flags(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        assert _calc_logging_level_from_verbosity_namespace(args) == DONE

    def test_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        assert _calc_logging_level_from_verbosity_namespace(args) == logging.INFO

    def test_v2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        assert _calc_logging_level_from_verbosity_namespace(args) == ENTER

    def test_combined_vv_verbose_qq_net_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv", "--verbose", "-qq"])
        assert _calc_logging_level_from_verbosity_namespace(args) == logging.INFO

    def test_quiet(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["--quiet"])
        assert (
            _calc_logging_level_from_verbosity_namespace(args) == logging.WARNING
        )
