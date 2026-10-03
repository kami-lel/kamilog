"""
dof-common-prefix_test.py

tests for `_DiffOnlyEngine._update_common` in `kamilog`
"""

from collections import deque

from kamilog.diff_only import _DiffOnlyEngine


def _make_engine(history):
    engine = _DiffOnlyEngine.__new__(_DiffOnlyEngine)
    lines = [m.split("\n") for m in history]
    engine._history = deque(lines, maxlen=max(len(history), 1))
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
        assert engine._common[0] == ["a", "b", "c"]


class TestUpdateCommonMultipleMessages:
    def test_identical_messages_mark_every_position_common(_):
        engine = _make_engine(["xyz", "xyz"])
        engine._update_common()
        assert engine._common[0] == ["x", "y", "z"]

    def test_divergent_position_becomes_none(_):
        engine = _make_engine(["abc", "abd"])
        engine._update_common()
        assert engine._common[0] == ["a", "b", None]

    def test_differing_lengths_mark_extra_positions_none(_):
        engine = _make_engine(["abc", "abcd"])
        engine._update_common()
        assert engine._common[0] == ["a", "b", "c", None]

    def test_three_messages_requires_all_to_agree(_):
        engine = _make_engine(["abc", "abd", "abc"])
        engine._update_common()
        assert engine._common[0] == ["a", "b", None]


class TestUpdateCommonMultiLine:
    def test_one_common_list_per_line_index(_):
        engine = _make_engine(["ab\ncd", "ab\nce"])
        engine._update_common()
        assert engine._common == [["a", "b"], ["c", None]]

    def test_line_missing_from_a_message_has_empty_common(_):
        engine = _make_engine(["ab\ncd", "ab"])
        engine._update_common()
        assert engine._common == [["a", "b"], []]

    def test_extra_line_in_later_message_has_empty_common(_):
        engine = _make_engine(["ab", "ab\ncd"])
        engine._update_common()
        assert engine._common == [["a", "b"], []]

    def test_lines_compared_by_index_not_by_content(_):
        engine = _make_engine(["ab\ncd", "cd\nab"])
        engine._update_common()
        assert engine._common == [[None, None], [None, None]]

    def test_line_lengths_differ_per_line(_):
        engine = _make_engine(["a\nxyz", "a\nxy"])
        engine._update_common()
        assert engine._common == [["a"], ["x", "y", None]]

    def test_empty_line_is_an_empty_common_list(_):
        engine = _make_engine(["a\n\nb", "a\n\nb"])
        engine._update_common()
        assert engine._common == [["a"], [], ["b"]]

    def test_single_line_history_has_one_entry(_):
        engine = _make_engine(["abc", "abc"])
        engine._update_common()
        assert len(engine._common) == 1
