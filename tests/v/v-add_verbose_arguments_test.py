"""
v-add_verbose_arguments_test.py

tests for `add_verbose_arguments` in `kamilog.py`
"""

from argparse import ArgumentParser
from kamilog.kamilog import add_verbose_arguments


class TestAddVerboseArguments:
    def test_default_args_have_zero_verbose_and_quiet(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        assert hasattr(args, "verbose")
        assert hasattr(args, "quiet")
        assert args.verbose == 0
        assert args.quiet == 0

    def test_vv_sets_verbose_to_2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        assert args.verbose == 2
        assert args.quiet == 0

    def test_quiet_flag_sets_quiet_to_1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["--quiet"])
        assert args.verbose == 0
        assert args.quiet == 1

    def test_combined_flags_accumulate(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv", "--verbose", "-qq"])
        assert args.verbose == 3
        assert args.quiet == 2
