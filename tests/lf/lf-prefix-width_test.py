"""
lf-prefix-width_test.py

tests for `_LogFormatEngine.count_prefix_chars` in `kamilog.py`
"""

import logging

from kamilog.kamilog import DATEFMT_TIME, _LogFormatEngine


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text


def _make_record(name, levelno=logging.INFO, msg="hello"):
    return logging.LogRecord(name, levelno, "path", 1, msg, (), None)


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
