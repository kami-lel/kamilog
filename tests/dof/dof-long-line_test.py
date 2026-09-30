"""
dof-long-line_test.py

tests for the long-line rule in `_DiffOnlyEngine` in `kamilog.py`
"""

import logging

import pytest

from kamilog.kamilog import (
    DATEFMT_TIME,
    _DiffOnlyEngine,
    _LogFormatEngine,
)


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text

    def color_badge(self, text, badge):
        return text


class TestLongLineWidthHelper:
    def test_limit_constant_is_100(_):
        assert _DiffOnlyEngine._LONG_LINE_COLS == 100

    @pytest.mark.parametrize(
        "width, expected", [(99, False), (100, False), (101, True)]
    )
    def test_boundary_with_no_prefix(_, width, expected):
        assert _DiffOnlyEngine._is_long_line("x" * width, 0) is expected

    @pytest.mark.parametrize(
        "width, expected", [(59, False), (60, False), (61, True)]
    )
    def test_prefix_counts_toward_width(_, width, expected):
        assert _DiffOnlyEngine._is_long_line("x" * width, 40) is expected

    def test_embedded_tab_expands_to_next_stop(_):
        # "abc" ends col 3, tab jumps to 8, then 92 more = 100
        assert _DiffOnlyEngine._is_long_line("abc\t" + "x" * 92, 0) is False
        assert _DiffOnlyEngine._is_long_line("abc\t" + "x" * 93, 0) is True

    def test_embedded_tab_respects_start_column(_):
        # starts col 5: "a" → 6, tab → 8, then 92 more = 100
        assert _DiffOnlyEngine._is_long_line("a\t" + "x" * 92, 5) is False
        assert _DiffOnlyEngine._is_long_line("a\t" + "x" * 93, 5) is True

    def test_tab_on_a_stop_advances_a_full_block(_):
        # 8 chars end on col 8; tab → 16
        head = "x" * 8 + "\t"
        assert _DiffOnlyEngine._is_long_line(head + "y" * 84, 0) is False
        assert _DiffOnlyEngine._is_long_line(head + "y" * 85, 0) is True

    def test_empty_line_is_short(_):
        assert _DiffOnlyEngine._is_long_line("", 0) is False

    def test_prefix_alone_over_limit_is_long(_):
        assert _DiffOnlyEngine._is_long_line("", 101) is True


class TestLongLineWidthWithRealPrefix:
    @staticmethod
    def _prefix(badges):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        record = logging.LogRecord("x", 20, "p", 1, "m", (), None)
        record.badges = badges
        return engine.count_prefix_chars(record)

    def test_badges_push_line_over_the_limit(self):
        plain = self._prefix(())
        badged = self._prefix(("dry", "yes"))
        room = 100 - plain
        line = "x" * room
        assert _DiffOnlyEngine._is_long_line(line, plain) is False
        assert _DiffOnlyEngine._is_long_line(line, badged) is True
