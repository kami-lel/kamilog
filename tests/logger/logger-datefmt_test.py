"""
logger-datefmt_test.py

tests for `_LogFormatEngine.format_time` datetime formats in `kamilog.py`
"""

import re

from kamilog.kamilog import (
    DATEFMT_DATETIME,
    DATEFMT_DATETIME_MS,
    DATEFMT_TIME,
    DATEFMT_TIME_MS,
    _LogFormatEngine,
)


class _StubPalette:
    def color_grey(self, text):
        return text


class _StubRecord:
    def __init__(self, created, msecs=207.0):
        self.created = created
        self.msecs = msecs


class TestDatefmtTime:
    def test_matches_hh_mm_ss(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME)
        out = engine.format_time(_StubRecord(1000.0))
        assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", out)


class TestDatefmtTimeMs:
    def test_matches_hh_mm_ss_with_milliseconds(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_TIME_MS)
        out = engine.format_time(_StubRecord(1000.0, msecs=207.0))
        assert re.fullmatch(r"\d{2}:\d{2}:\d{2}\.\d{3}", out)
        assert out.endswith(".207")


class TestDatefmtDatetime:
    def test_matches_full_datetime(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_DATETIME)
        out = engine.format_time(_StubRecord(1000.0))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", out)


class TestDatefmtDatetimeMs:
    def test_matches_full_datetime_with_milliseconds(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=DATEFMT_DATETIME_MS)
        out = engine.format_time(_StubRecord(1000.0, msecs=207.0))
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", out
        )
        assert out.endswith(".207")


class TestDatefmtDisabled:
    def test_none_datefmt_returns_empty_string(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.format_time(_StubRecord(1000.0)) == ""


class TestRelativeTimeOverridesDatefmt:
    def test_zero_delta_is_all_zero_with_plus_sign(_):
        engine = _LogFormatEngine(
            _StubPalette(), datefmt=DATEFMT_TIME, relative_to=1000.0
        )
        assert engine.format_time(_StubRecord(1000.0)) == "+00:00:00.000"

    def test_positive_delta_has_plus_sign(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        assert engine.format_time(_StubRecord(1005.5)) == "+00:00:05.500"

    def test_negative_delta_has_minus_sign(_):
        engine = _LogFormatEngine(_StubPalette(), relative_to=1000.0)
        assert engine.format_time(_StubRecord(994.25)) == "-00:00:05.750"
