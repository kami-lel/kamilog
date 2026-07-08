"""
dof-common-prefix_test.py

tests for `_DiffOnlyEngine._update_common` in `kamilog.py`
"""

from collections import deque

from kamilog.kamilog import _DiffOnlyEngine


def _make_engine(history):
    engine = _DiffOnlyEngine.__new__(_DiffOnlyEngine)
    engine._history = deque(history, maxlen=max(len(history), 1))
    return engine


class TestUpdateCommonEmptyHistory:
    def test_empty_history_gives_empty_common(_):
        engine = _make_engine([])
        engine._update_common()
        assert engine._common == []


class TestUpdateCommonSingleMessage:
    def test_single_message_marks_every_position_common(_):
        engine = _make_engine(["abc"])
        engine._update_common()
        assert engine._common == ["a", "b", "c"]


class TestUpdateCommonMultipleMessages:
    def test_identical_messages_mark_every_position_common(_):
        engine = _make_engine(["xyz", "xyz"])
        engine._update_common()
        assert engine._common == ["x", "y", "z"]

    def test_divergent_position_becomes_none(_):
        engine = _make_engine(["abc", "abd"])
        engine._update_common()
        assert engine._common == ["a", "b", None]

    def test_differing_lengths_mark_extra_positions_none(_):
        engine = _make_engine(["abc", "abcd"])
        engine._update_common()
        assert engine._common == ["a", "b", "c", None]

    def test_three_messages_requires_all_to_agree(_):
        engine = _make_engine(["abc", "abd", "abc"])
        engine._update_common()
        assert engine._common == ["a", "b", None]
