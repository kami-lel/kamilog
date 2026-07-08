"""
lf-relative-time_test.py

tests for `_LogFormatEngine` relative-time prefix width and precedence
over `datefmt` in `kamilog.py`
"""

import logging

from kamilog.kamilog import DATEFMT_DATETIME, _LogFormatEngine


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text


def _make_record(name, created, levelno=logging.INFO, msg="hi"):
    record = logging.LogRecord(name, levelno, "path", 1, msg, (), None)
    record.created = created
    return record


class TestRelativeTimeTakesPrecedenceOverDatefmt:
    def test_relative_to_overrides_datefmt_format(_):
        engine = _LogFormatEngine(
            _StubPalette(), datefmt=DATEFMT_DATETIME, relative_to=1000.0
        )
        line = engine.build_line(_make_record("root", 1005.5))
        assert line.startswith("+00:00:05.500")


class TestRelativeTimePrefixWidthMatchesRenderedLine:
    def test_prefix_width_matches_message_start_for_zero_delta(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        record = _make_record("mymodule", 1000.0)
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hi"

    def test_prefix_width_matches_message_start_for_positive_delta(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        record = _make_record("mymodule", 1005.5)
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hi"

    def test_prefix_width_matches_message_start_for_negative_delta(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        record = _make_record("mymodule", 994.25)
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hi"

    def test_prefix_width_matches_message_start_on_root_logger(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        record = _make_record("root", 1005.5)
        line = engine.build_line(record)
        assert line[engine.count_prefix_chars(record) :] == "hi"


class TestRelativeTimeExactPrefixValue:
    def test_named_logger_prefix_width(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        record = _make_record("mymodule", 1005.5)
        assert engine.count_prefix_chars(record) == 30
