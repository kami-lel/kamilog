"""
tests function related to verbosity & logging level

ie
add_verbose_arguments, calc_logging_level_from_verbosity,
calc_logging_level_from_verbosity_namespace,
set_logging_level_by_verbosity
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
    _calc_logging_level_from_verbosity,
    _calc_logging_level_from_verbosity_namespace,
    set_logging_level_by_verbosity,
    SUCC,
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


class TestCalcLoggingLevel:
    """
    test ``calc_logging_level_from_verbosity`` integer mapping
    """

    def test_zero(_):
        level = _calc_logging_level_from_verbosity(0)
        print(level)
        assert level == DONE  # 25

    def test_v1(_):
        level = _calc_logging_level_from_verbosity(1)
        print(level)
        assert level == logging.INFO  # 20

    def test_v2(_):
        level = _calc_logging_level_from_verbosity(2)
        print(level)
        assert level == SUCC  # 15

    def test_v3(_):
        level = _calc_logging_level_from_verbosity(3)
        print(level)
        assert level == logging.DEBUG  # 10

    def test_v_over(_):
        level = _calc_logging_level_from_verbosity(99)
        print(level)
        assert level == logging.DEBUG  # 10

    def test_q1(_):
        level = _calc_logging_level_from_verbosity(-1)
        print(level)
        assert level == logging.WARNING  # 30

    def test_q2(_):
        level = _calc_logging_level_from_verbosity(-2)
        print(level)
        assert level == logging.ERROR  # 40

    def test_q3(_):
        level = _calc_logging_level_from_verbosity(-3)
        print(level)
        assert level == logging.CRITICAL  # 50


class TestCalcLoggingLevelNamespace:
    """
    test ``calc_logging_level_from_verbosity_namespace``
    """

    def test_no(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args([])
        level = _calc_logging_level_from_verbosity_namespace(args)
        print(level)
        assert level == DONE

    def test_v1(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-v"])
        level = _calc_logging_level_from_verbosity_namespace(args)
        print(level)
        assert level == logging.INFO

    def test_v2(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv"])
        level = _calc_logging_level_from_verbosity_namespace(args)
        print(level)
        assert level == SUCC

    def test_vv_mixed(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["-vv", "--verbose", "-qq"])  # net=1
        level = _calc_logging_level_from_verbosity_namespace(args)
        print(level)
        assert level == logging.INFO

    def test_quiet(_):
        parser = ArgumentParser()
        add_verbose_arguments(parser)
        args = parser.parse_args(["--quiet"])
        level = _calc_logging_level_from_verbosity_namespace(args)
        print(level)
        assert level == logging.WARNING


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
        assert logging_level == SUCC  # 15, not DEBUG

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

    # test calc_logging_level_from_verbosity_namespace
    level = _calc_logging_level_from_verbosity_namespace(args)
    print("logging level:\t{}".format(level))

    # test set_logging_level_by_verbosity
    set_logging_level_by_verbosity(args, logger_name=LOGGER_NAME)

    logger = logging.getLogger(LOGGER_NAME)
    print("logger level:\t{}".format(logger.level))
