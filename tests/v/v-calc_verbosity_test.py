"""
v-calc_verbosity_test.py

tests for `calc_verbosity` in `kamilog.py`
"""

from argparse import ArgumentParser
from kamilog.kamilog import add_verbose_arguments, calc_verbosity


class TestCalcVerbosity:
    def test_no_flags(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        assert calc_verbosity(args) == 0

    def test_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        assert calc_verbosity(args) == 1

    def test_v2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        assert calc_verbosity(args) == 2

    def test_combined_vv_verbose_qq_net_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv", "--verbose", "-qq"])
        assert calc_verbosity(args) == 1

    def test_quiet(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["--quiet"])
        assert calc_verbosity(args) == -1

    def test_base_verbosity_offset(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        assert calc_verbosity(args, verbosity=2) == 3
