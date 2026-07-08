"""
ansi-disable-color_test.py

tests for `AnsiRenderer`'s explicit `is_disabled` override in `kamilog.py`
"""

from kamilog.kamilog import AnsiColor, AnsiRenderer


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


class TestDisabledOverridesTtyStream:
    def test_tty_stream_with_is_disabled_stays_uncolored(_):
        renderer = AnsiRenderer(_FakeStream(True), is_disabled=True)
        assert renderer.color("hi", AnsiColor.RED) == "hi"


class TestDisabledWithNoneStream:
    def test_none_stream_with_is_disabled_stays_uncolored(_):
        renderer = AnsiRenderer(None, is_disabled=True)
        assert renderer.color("hi", AnsiColor.RED) == "hi"


class TestNotDisabledKeepsTtyBehavior:
    def test_tty_stream_without_is_disabled_is_colored(_):
        renderer = AnsiRenderer(_FakeStream(True), is_disabled=False)
        assert renderer.color("hi", AnsiColor.RED) == "\033[31mhi\033[0m"


class TestIsDisabledDefaultsToFalse:
    def test_default_is_disabled_does_not_suppress_tty_color(_):
        renderer = AnsiRenderer(_FakeStream(True))
        assert renderer.color("hi", AnsiColor.RED) == "\033[31mhi\033[0m"
