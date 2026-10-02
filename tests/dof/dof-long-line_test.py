"""
dof-long-line_test.py

tests for the long-line rule in `_DiffOnlyEngine` in `kamilog`
"""

import logging

import pytest

from kamilog import DATEFMT_TIME
from kamilog.diff_only import _DiffOnlyEngine
from kamilog.formatter import _LogFormatEngine


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


class _StubEngine:
    def count_prefix_chars(self, record):
        return 0


class _StubFormatter:
    def __init__(self):
        self.engine = _StubEngine()
        self.palette = _StubPalette()


class _StubRecord:
    def __init__(self, message):
        self._message = message

    def getMessage(self):
        return self._message


class _SpyEngine(_DiffOnlyEngine):
    """records the long-line flag handed to every rendered run"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = []

    def _render_run(self, message, run_s, run_e, prefix_len, is_long):
        self.flags.append(is_long)
        return super()._render_run(message, run_s, run_e, prefix_len, is_long)


def _spy_second(first, second):
    engine = _SpyEngine(_StubFormatter(), threshold=1)
    engine.process(_StubRecord(first))
    out = engine.process(_StubRecord(second))
    return engine.flags, out


_SHORT = "a" * 16 + "/bbb"
_LONG = "a" * 60 + "/" + "b" * 60


class TestLongFlagPerLine:
    def test_short_line_flag_is_false(_):
        flags, _out = _spy_second(_SHORT + "X", _SHORT + "Y")
        assert flags == [False]

    def test_long_line_flag_is_true(_):
        flags, _out = _spy_second(_LONG + "X", _LONG + "Y")
        assert flags == [True]

    def test_flag_is_decided_per_physical_line(_):
        first = _SHORT + "X\n" + _LONG + "X\n" + _SHORT + "X"
        second = _SHORT + "Y\n" + _LONG + "Y\n" + _SHORT + "Y"
        flags, _out = _spy_second(first, second)
        assert flags == [False, True, False]

    def test_output_is_byte_identical_to_before(_):
        _flags, out = _spy_second(_LONG + "X", _LONG + "Y")
        plain = _DiffOnlyEngine(_StubFormatter(), threshold=1)
        plain.process(_StubRecord(_LONG + "X"))
        assert out == plain.process(_StubRecord(_LONG + "Y"))


class _NoLimitEngine(_DiffOnlyEngine):
    _LONG_LINE_COLS = 10**6


def _second_of_width(width, engine_cls=_DiffOnlyEngine):
    """compress a message of exactly ``width`` columns, prefix 0"""
    body = "a" * (width - 5) + "/bbb"
    engine = engine_cls(_StubFormatter(), threshold=1)
    engine.process(_StubRecord(body + "X"))
    return engine.process(_StubRecord(body + "Y"))


class TestSpacedFullBlockDittos:
    def test_line_of_100_columns_keeps_tab_form(_):
        out = _second_of_width(100)
        assert out.startswith("〃\t〃\t")
        assert "〃 〃" not in out

    def test_line_of_101_columns_uses_spaced_form(_):
        out = _second_of_width(101)
        assert out.startswith("〃 〃 ")
        assert "〃\t" not in out

    def test_short_line_output_is_unchanged(_):
        assert _second_of_width(40) == "〃\t〃\t〃\t〃\t〃 /bbbY"

    def test_long_line_is_narrower_than_its_tab_form(_):
        long_form = _second_of_width(160)
        tab_form = _second_of_width(160, _NoLimitEngine)
        assert len(long_form.expandtabs(8)) < len(tab_form.expandtabs(8))

    def test_each_full_block_is_marker_plus_one_space(_):
        out = _second_of_width(160)
        assert out.startswith("〃 " * 5)
        assert out.endswith("Y")

    def test_multi_line_message_mixes_forms_per_line(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=1)
        short = "a" * 16 + "/bbb"
        long = "a" * 120 + "/bbb"
        engine.process(_StubRecord(short + "X\n" + long + "X"))
        out = engine.process(_StubRecord(short + "Y\n" + long + "Y"))
        line1, line2 = out.split("\n")
        assert line1.startswith("〃\t") and "〃 〃" not in line1
        assert line2.startswith("〃 〃 ") and "〃\t" not in line2


class _PrefixEngine:
    def __init__(self, prefix_len):
        self._prefix_len = prefix_len

    def count_prefix_chars(self, record):
        return self._prefix_len


class _PrefixFormatter:
    def __init__(self, prefix_len):
        self.engine = _PrefixEngine(prefix_len)
        self.palette = _StubPalette()


def _second_with_prefix(width, prefix_len):
    """compress a line whose message is ``width`` columns wide"""
    body = "a" * (width - 5) + "/bbb"
    engine = _DiffOnlyEngine(_PrefixFormatter(prefix_len), threshold=1)
    engine.process(_StubRecord(body + "X"))
    return engine.process(_StubRecord(body + "Y"))


class TestSpacedLeaderAndGapDittos:
    @pytest.mark.parametrize("prefix_len", range(0, 9))
    @pytest.mark.parametrize("width", range(110, 121))
    def test_long_line_has_no_tabs_or_padding_runs(_, width, prefix_len):
        out = _second_with_prefix(width, prefix_len)
        assert "\t" not in out
        assert "  " not in out

    @pytest.mark.parametrize("prefix_len", range(0, 9))
    @pytest.mark.parametrize("width", range(110, 121))
    def test_long_line_keeps_its_tail(_, width, prefix_len):
        assert _second_with_prefix(width, prefix_len).endswith("/bbbY")

    def test_leader_at_minimum_earns_a_spaced_marker(_):
        # prefix 4: leader of 4 chars (== _LEADER_MARKER_MIN)
        with_leader = _second_with_prefix(110, 4)
        # prefix 5: leader of 3 chars, dropped instead of a bare tab
        short_leader = _second_with_prefix(110, 5)
        assert with_leader.count("〃 ") == short_leader.count("〃 ") + 1

    def test_short_leader_is_dropped_not_tabbed(_):
        out = _second_with_prefix(110, 6)
        assert not out.startswith("\t")
        assert out.startswith("〃 ")

    def test_short_line_keeps_leader_tab_and_gap_padding(_):
        engine = _DiffOnlyEngine(_PrefixFormatter(5), threshold=1)
        body = "a" * 25 + "/bbb"
        engine.process(_StubRecord(body + "X"))
        assert engine.process(_StubRecord(body + "Y")) == (
            "\t〃\t〃\t〃    /bbbY"
        )

    def test_gap_of_marker_width_or_more_becomes_one_spaced_marker(_):
        # every long output ends "<marker> <tail>" or "<block> <tail>";
        # the tail is always preceded by exactly one space
        for width in range(110, 121):
            out = _second_with_prefix(width, 0)
            assert out.endswith("〃 /bbbY")
