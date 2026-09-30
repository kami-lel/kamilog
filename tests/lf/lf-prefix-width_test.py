"""
lf-prefix-width_test.py

tests for `_LogFormatEngine.count_prefix_chars` in `kamilog.py`
"""

import logging

import pytest

from kamilog.kamilog import DATEFMT_TIME, _LogFormatEngine


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text

    def color_badge(self, text, badge):
        return text


def _make_record(name, levelno=logging.INFO, msg="hello", badges=None):
    record = logging.LogRecord(name, levelno, "path", 1, msg, (), None)
    if badges is not None:
        record.badges = badges
    return record


class TestPrefixWidthMatchesRenderedLine:
    def test_root_name_without_timestamp(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("root")
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hello"

    def test_root_name_with_timestamp(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        record = _make_record("root")
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hello"

    def test_named_logger_without_timestamp(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("mymodule")
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hello"

    def test_named_logger_with_timestamp(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        record = _make_record("mymodule")
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hello"


class TestPrefixWidthExactValues:
    def test_root_no_timestamp_is_seven(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.count_prefix_chars(_make_record("root")) == 7

    def test_root_with_timestamp_adds_nine(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        assert engine.count_prefix_chars(_make_record("root")) == 16

    def test_named_no_timestamp_adds_name_and_space(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.count_prefix_chars(_make_record("mymodule")) == 16

    def test_named_with_timestamp(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        assert engine.count_prefix_chars(_make_record("mymodule")) == 25


class TestPrefixWidthEmptyOrNoneName:
    def test_empty_name_behaves_like_root(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.count_prefix_chars(_make_record("")) == 7

    def test_none_name_behaves_like_root(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.count_prefix_chars(_make_record(None)) == 7


class TestPrefixWidthWithBadges:
    @pytest.mark.parametrize("datefmt", [None, DATEFMT_TIME])
    @pytest.mark.parametrize("name", ["root", "mymodule"])
    @pytest.mark.parametrize(
        "badges",
        [
            (),
            ("dry",),
            ("dry", "yes"),
            ("force", "dry", "auto"),
            ("unsafe", "force", "retries", "deploy-staging"),
        ],
    )
    def test_message_starts_at_prefix_column(_, badges, name, datefmt):
        engine = _LogFormatEngine(_StubPalette(), datefmt=datefmt)
        record = _make_record(name, badges=badges)
        line = engine.build_line(record).expandtabs(8)
        assert line[engine.count_prefix_chars(record) :] == "hello"

    def test_root_no_timestamp_one_badge(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("root", badges=("dry",))
        assert engine.count_prefix_chars(record) == 15

    def test_named_no_timestamp_one_badge(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("mymodule", badges=("dry",))
        assert engine.count_prefix_chars(record) == 24

    def test_root_with_timestamp_one_badge(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        record = _make_record("root", badges=("dry",))
        assert engine.count_prefix_chars(record) == 23

    def test_badge_ending_before_stop_uses_that_stop(_):
        # 7 chars end at col 7, level on stop 8, then 5 + ":" + a space
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("root", badges=("retries",))
        assert engine.count_prefix_chars(record) == 15

    def test_badge_ending_on_stop_pushes_level_a_full_stop(_):
        # 8 chars end on col 8, strictly after gives stop 16
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        record = _make_record("root", badges=("abcdefgh",))
        assert engine.count_prefix_chars(record) == 23

    def test_empty_badges_same_as_none(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        with_empty = _make_record("mymodule", badges=())
        without = _make_record("mymodule")
        assert engine.count_prefix_chars(
            with_empty
        ) == engine.count_prefix_chars(without)
