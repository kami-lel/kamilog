"""
ansi-tty-detect_test.py

tests for `AnsiRenderer` TTY auto-detection in `kamilog.py`
"""

from kamilog.kamilog import AnsiColor, AnsiRenderer


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


class _StreamWithoutIsatty:
    pass


class TestNoneStreamDisablesColor:
    def test_color_returns_text_unchanged(_):
        renderer = AnsiRenderer(None)
        assert renderer.color("hi", AnsiColor.RED) == "hi"


class TestTtyStreamEnablesColor:
    def test_color_wraps_text_with_ansi_codes(_):
        renderer = AnsiRenderer(_FakeStream(True))
        assert renderer.color("hi", AnsiColor.RED) == "\033[31mhi\033[0m"


class TestNonTtyStreamDisablesColor:
    def test_color_returns_text_unchanged(_):
        renderer = AnsiRenderer(_FakeStream(False))
        assert renderer.color("hi", AnsiColor.RED) == "hi"


class TestStreamWithoutIsattyDisablesColor:
    def test_color_returns_text_unchanged(_):
        renderer = AnsiRenderer(_StreamWithoutIsatty())
        assert renderer.color("hi", AnsiColor.RED) == "hi"


class TestDefaultStreamIsNone:
    def test_constructing_without_stream_disables_color(_):
        renderer = AnsiRenderer()
        assert renderer.color("hi", AnsiColor.RED) == "hi"
