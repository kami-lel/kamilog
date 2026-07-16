"""
v-calc_logging_level_namespace_test.py

tests for `calc_logging_level`'s `namespace` param in `kamilog.py`
"""

import logging
from argparse import ArgumentParser
from kamilog.kamilog import (
    add_verbose_arguments,
    calc_logging_level,
    ENTER,
    DONE,
)


class TestCalcLoggingLevelNamespace:
    def test_no_flags(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        assert calc_logging_level(0, namespace=args) == DONE

    def test_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        assert calc_logging_level(0, namespace=args) == logging.INFO

    def test_v2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        assert calc_logging_level(0, namespace=args) == ENTER

    def test_combined_vv_verbose_qq_net_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv", "--verbose", "-qq"])
        assert calc_logging_level(0, namespace=args) == logging.INFO

    def test_quiet(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["--quiet"])
        assert calc_logging_level(0, namespace=args) == logging.WARNING

    def test_base_verbosity_offset(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        assert calc_logging_level(1, namespace=args) == ENTER

    def test_namespace_none_uses_plain_verbosity(_):
        assert calc_logging_level(1, namespace=None) == logging.INFO
