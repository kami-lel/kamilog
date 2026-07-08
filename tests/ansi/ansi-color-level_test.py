"""
ansi-color-level_test.py

tests for `AnsiRenderer.color_level` and `color_grey` in `kamilog.py`
"""

import logging

from kamilog.kamilog import AnsiRenderer, _CustomLogLevel


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


def _enabled_renderer():
    return AnsiRenderer(_FakeStream(True))


class TestColorLevelAppliesBoldAndMappedColor:
    def test_debug_uses_cyan(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("DEBUG", logging.DEBUG)
            == "\033[1m\033[36mDEBUG\033[0m"
        )

    def test_warning_uses_yellow(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("WARN.", logging.WARNING)
            == "\033[1m\033[33mWARN.\033[0m"
        )

    def test_error_uses_red(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("ERROR", logging.ERROR)
            == "\033[1m\033[31mERROR\033[0m"
        )

    def test_critical_uses_bright_magenta(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("CRIT.", logging.CRITICAL)
            == "\033[1m\033[95mCRIT.\033[0m"
        )


class TestColorLevelAppliesCustomLevelColors:
    def test_enter_uses_bright_cyan(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("ENTER", _CustomLogLevel.ENTER)
            == "\033[1m\033[96mENTER\033[0m"
        )

    def test_skip_uses_blue(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("SKIP ", _CustomLogLevel.SKIP)
            == "\033[1m\033[34mSKIP \033[0m"
        )

    def test_succ_uses_green(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("SUCC.", _CustomLogLevel.SUCC)
            == "\033[1m\033[32mSUCC.\033[0m"
        )

    def test_pass_uses_bright_green(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("PASS ", _CustomLogLevel.PASS)
            == "\033[1m\033[92mPASS \033[0m"
        )

    def test_done_uses_bright_yellow(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("DONE ", _CustomLogLevel.DONE)
            == "\033[1m\033[93mDONE \033[0m"
        )

    def test_fail_uses_bright_red(_):
        renderer = _enabled_renderer()
        assert (
            renderer.color_level("FAIL ", _CustomLogLevel.FAIL)
            == "\033[1m\033[91mFAIL \033[0m"
        )


class TestColorLevelUnmappedLevelIsUnchanged:
    def test_unknown_levelno_returns_text_as_is(_):
        renderer = _enabled_renderer()
        assert renderer.color_level("12345", 99999) == "12345"


class TestColorLevelRespectsDisabledState:
    def test_disabled_renderer_returns_text_unchanged(_):
        renderer = AnsiRenderer(_FakeStream(False))
        assert renderer.color_level("WARN.", logging.WARNING) == "WARN."


class TestColorGrey:
    def test_enabled_renderer_wraps_with_grey(_):
        renderer = _enabled_renderer()
        assert renderer.color_grey("hi") == "\033[90mhi\033[0m"

    def test_color_grey_does_not_apply_bold(_):
        renderer = _enabled_renderer()
        assert "\033[1m" not in renderer.color_grey("hi")

    def test_disabled_renderer_returns_text_unchanged(_):
        renderer = AnsiRenderer(_FakeStream(False))
        assert renderer.color_grey("hi") == "hi"
