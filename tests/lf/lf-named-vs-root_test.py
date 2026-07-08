"""
lf-named-vs-root_test.py

tests for `_LogFormatEngine` source-label rendering (named vs. root
logger) in `kamilog.py`
"""

import logging

from kamilog.kamilog import _LogFormatEngine


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text


def _make_record(name, msg="hello"):
    return logging.LogRecord(name, logging.INFO, "path", 1, msg, (), None)


class TestRootLoggerSourceLabel:
    def test_root_renders_bare_colon(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        line = engine.build_line(_make_record("root"))
        assert line == "INFO : hello"

    def test_root_has_no_extra_space_before_colon(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        line = engine.build_line(_make_record("root"))
        assert "  " not in line


class TestNamedLoggerSourceLabel:
    def test_named_logger_renders_name_and_colon(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        line = engine.build_line(_make_record("mymodule"))
        assert line == "INFO  mymodule: hello"

    def test_named_logger_has_space_before_name(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        line = engine.build_line(_make_record("mymodule"))
        assert line.split("mymodule")[0].endswith("  ")


class TestEmptyOrNoneNameMatchesRoot:
    def test_empty_string_name_matches_root_rendering(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.build_line(_make_record("")) == "INFO : hello"

    def test_none_name_matches_root_rendering(_):
        engine = _LogFormatEngine(_StubPalette(), datefmt=None)
        assert engine.build_line(_make_record(None)) == "INFO : hello"


class TestSourceColoringCallsPalette:
    def test_root_colors_only_the_colon(_):
        calls = []

        class RecordingPalette:
            def color_grey(self, text):
                calls.append(text)
                return text

            def color_level(self, text, levelno):
                return text

        engine = _LogFormatEngine(RecordingPalette(), datefmt=None)
        engine.build_line(_make_record("root"))
        assert calls == [":"]

    def test_named_colors_name_and_colon_separately(_):
        calls = []

        class RecordingPalette:
            def color_grey(self, text):
                calls.append(text)
                return text

            def color_level(self, text, levelno):
                return text

        engine = _LogFormatEngine(RecordingPalette(), datefmt=None)
        engine.build_line(_make_record("mymodule"))
        assert calls == ["mymodule", ":"]
