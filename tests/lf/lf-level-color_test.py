"""
lf-level-color_test.py

tests for `_LogFormatEngine._fmt_level` padding and colorization in
`kamilog.py`
"""

import logging

from kamilog.kamilog import _CustomLogLevel, _LogFormatEngine


class _RecordingPalette:
    def __init__(self):
        self.level_calls = []

    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        self.level_calls.append((text, levelno))
        return text


def _make_record(levelno, name="x", msg="m"):
    return logging.LogRecord(name, levelno, "path", 1, msg, (), None)


class TestStandardLevelPadding:
    def test_debug_is_five_chars(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.DEBUG))
        assert palette.level_calls == [("DEBUG", logging.DEBUG)]

    def test_info_pads_with_trailing_space(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.INFO))
        assert palette.level_calls == [("INFO ", logging.INFO)]

    def test_warning_is_truncated_to_warn_dot(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.WARNING))
        assert palette.level_calls == [("WARN.", logging.WARNING)]

    def test_error_is_five_chars(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.ERROR))
        assert palette.level_calls == [("ERROR", logging.ERROR)]

    def test_critical_is_truncated_to_crit_dot(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.CRITICAL))
        assert palette.level_calls == [("CRIT.", logging.CRITICAL)]


class TestCustomLevelPadding:
    def test_enter_needs_no_padding(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(_CustomLogLevel.ENTER))
        assert palette.level_calls == [("ENTER", _CustomLogLevel.ENTER)]

    def test_skip_pads_with_trailing_space(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(_CustomLogLevel.SKIP))
        assert palette.level_calls == [("SKIP ", _CustomLogLevel.SKIP)]

    def test_succ_uses_dot_padding(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(_CustomLogLevel.SUCC))
        assert palette.level_calls == [("SUCC.", _CustomLogLevel.SUCC)]

    def test_fail_pads_with_trailing_space(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(_CustomLogLevel.FAIL))
        assert palette.level_calls == [("FAIL ", _CustomLogLevel.FAIL)]


class TestUnknownLevelFallsBackToNumericPadding:
    def test_short_numeric_level_is_left_padded_to_five(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(7))
        assert palette.level_calls == [("7    ", 7)]

    def test_long_numeric_level_is_truncated_to_five(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(123456))
        assert palette.level_calls == [("12345", 123456)]


class TestColorLevelReceivesRawLevelno:
    def test_levelno_passed_through_unchanged(_):
        palette = _RecordingPalette()
        engine = _LogFormatEngine(palette, datefmt=None)
        engine.build_line(_make_record(logging.WARNING))
        _, passed_levelno = palette.level_calls[0]
        assert passed_levelno == logging.WARNING
