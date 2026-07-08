"""
logger-idempotent_test.py

tests for `getLogger` idempotent re-configuration in `kamilog.py`
"""

import uuid

from kamilog.kamilog import _DiffOnlyMsgFilter, getLogger


def _count_diff_only_filters(logger):
    return sum(1 for f in logger.filters if isinstance(f, _DiffOnlyMsgFilter))


class TestSameNameReturnsSameInstance:
    def test_repeated_calls_return_identical_logger(_):
        name = uuid.uuid4().hex
        first = getLogger(name)
        second = getLogger(name)
        assert first is second


class TestHandlersAreNotDuplicated:
    def test_handler_count_stays_two_after_second_call(_):
        name = uuid.uuid4().hex
        getLogger(name)
        logger = getLogger(name)
        assert len(logger.handlers) == 2

    def test_handler_count_stays_two_with_different_kwargs(_):
        name = uuid.uuid4().hex
        getLogger(name)
        logger = getLogger(name, disable_color=True)
        assert len(logger.handlers) == 2


class TestDiffOnlyFilterIsNotDuplicated:
    def test_filter_count_stays_one_after_second_call(_):
        name = uuid.uuid4().hex
        getLogger(name)
        logger = getLogger(name)
        assert _count_diff_only_filters(logger) == 1

    def test_filter_count_stays_one_with_different_kwargs(_):
        name = uuid.uuid4().hex
        getLogger(name)
        logger = getLogger(name, disable_diff_only_compression=True)
        assert _count_diff_only_filters(logger) == 1
