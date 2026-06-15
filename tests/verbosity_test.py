"""
tests function related to verbosity & logging level

ie
add_verbose_arguments, calc_verbosity, set_logging_level_by_verbosity
"""

from argparse import ArgumentParser
import sys
import os
import logging

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from kamilog.kamilog import (
    add_verbose_arguments,
    calc_verbosity,
    set_logging_level_by_verbosity,
    DONE,
)

# pytest candidates  ###########################################################


class TestAddVerboseArguments:
    """
    test ``add_verbose_arguments``
    """

    def test1(_):
        ARGS = []
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        print(args)

        assert hasattr(args, "verbose")
        assert hasattr(args, "quiet")

        assert args.verbose == 0
        assert args.quiet == 0

    def test2(_):
        ARGS = ["-vv"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        print(args)

        assert hasattr(args, "verbose")
        assert hasattr(args, "quiet")

        assert args.verbose == 2
        assert args.quiet == 0

    def test3(_):
        ARGS = ["--quiet"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        print(args)

        assert hasattr(args, "verbose")
        assert hasattr(args, "quiet")

        assert args.verbose == 0
        assert args.quiet == 1

    def test4(_):
        ARGS = ["-vv", "--verbose", "-qq"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        print(args)

        assert hasattr(args, "verbose")
        assert hasattr(args, "quiet")

        assert args.verbose == 3
        assert args.quiet == 2


class TestCalcVerbosity:
    """
    test ``calc_verbosity``
    """

    def test1(_):
        ARGS = []
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        verbosity = calc_verbosity(args)

        print(verbosity)
        assert verbosity == 0

    def test2(_):
        ARGS = ["-vv"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        verbosity = calc_verbosity(args)

        print(verbosity)
        assert verbosity == 2

    def test3(_):
        ARGS = ["--quiet"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        verbosity = calc_verbosity(args)

        print(verbosity)
        assert verbosity == -1

    def test4(_):
        ARGS = ["-vv", "--verbose", "-qq"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        verbosity = calc_verbosity(args)

        print(verbosity)
        assert verbosity == 1


class TestSLLBV:
    """
    test ``set_logging_level_by_verbosity``
    """

    def test_no(_):
        ARGS = []
        LOGGER_NAME = "TestSLLBV_test1"
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == DONE

    def test_v1(_):
        ARGS = ["-v"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == logging.INFO

    def test_v2(_):
        ARGS = ["-vv"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == logging.DEBUG

    def test_v3(_):
        ARGS = ["-vvv"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == logging.DEBUG

    def test_q1(_):
        ARGS = ["-q"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == logging.WARNING

    def test_q2(_):
        ARGS = ["-qq"]
        parser = ArgumentParser()

        add_verbose_arguments(parser)
        args = parser.parse_args(ARGS)

        set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)
        logger = logging.getLogger(LOGGER_NAME)
        logging_level = logger.level

        print(logging_level)
        assert logging_level == logging.ERROR


# sys.argv parser  #############################################################

LOGGER_NAME = "VERBOSITY_TEST"

sys_argv_parser = ArgumentParser()
add_verbose_arguments(sys_argv_parser)


if __name__ == "__main__":
    args = sys_argv_parser.parse_args()

    # test calc_verbosity
    verbosity = calc_verbosity(args)
    print("verbosity:\t{}".format(verbosity))

    # test set_logging_level_by_verbosity
    set_logging_level_by_verbosity(args, LOGGER_NAME)

    logger = logging.getLogger(LOGGER_NAME)
    print("logging level:\t{}".format(logger.level))
