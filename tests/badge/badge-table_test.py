"""
badge-table_test.py

tests for `NATIVE_BADGES` in `kamilog`
"""

import pytest

from kamilog import AnsiStyle
from kamilog.badges import NATIVE_BADGES

_EXPECTED = {
    "dry": AnsiStyle.BRIGHT_MAGENTA,
    "chk": AnsiStyle.BRIGHT_BLUE,
    "mock": AnsiStyle.CYAN,
    "sandbox": AnsiStyle.BRIGHT_CYAN,
    "force": AnsiStyle.BRIGHT_YELLOW,
    "undo": AnsiStyle.RED,
    "grant": AnsiStyle.BRIGHT_YELLOW,
    "elevated": AnsiStyle.BRIGHT_YELLOW,
    "legacy": AnsiStyle.YELLOW,
    "unstable": AnsiStyle.YELLOW,
    "new": AnsiStyle.BRIGHT_GREEN,
    "edit": AnsiStyle.BRIGHT_GREEN,
    "owr": AnsiStyle.RED,
    "del": AnsiStyle.RED,
    "mv": AnsiStyle.BRIGHT_GREEN,
    "cp": AnsiStyle.BRIGHT_GREEN,
    "cached": AnsiStyle.MAGENTA,
    "stale": AnsiStyle.YELLOW,
    "auto": AnsiStyle.BLUE,
    "fresh": AnsiStyle.GREEN,
    "resume": AnsiStyle.GREEN,
    "offline": AnsiStyle.YELLOW,
    "watch": AnsiStyle.BRIGHT_BLUE,
    "bg": AnsiStyle.BLUE,
    "retry": AnsiStyle.BRIGHT_MAGENTA,
    "fallback": AnsiStyle.BRIGHT_YELLOW,
    "timeout": AnsiStyle.BRIGHT_RED,
    "abort": AnsiStyle.BRIGHT_RED,
}


class TestNativeBadgeTable:
    def test_has_exactly_the_documented_badges(_):
        assert set(NATIVE_BADGES) == set(_EXPECTED)

    @pytest.mark.parametrize("label", sorted(_EXPECTED))
    def test_hue(_, label):
        assert NATIVE_BADGES[label] == _EXPECTED[label]
