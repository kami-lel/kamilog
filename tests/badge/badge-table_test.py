"""
badge-table_test.py

tests for `_NATIVE_BADGES` in `kamilog`
"""

import pytest

from kamilog import AnsiStyle
from kamilog.badges import _NATIVE_BADGES

_EXPECTED = {
    "dry": (AnsiStyle.BRIGHT_MAGENTA, 73),
    "chk": (AnsiStyle.BRIGHT_BLUE, 68),
    "mock": (AnsiStyle.CYAN, 67),
    "sandbox": (AnsiStyle.BRIGHT_CYAN, 53),
    "force": (AnsiStyle.BRIGHT_YELLOW, 84),
    "undo": (AnsiStyle.RED, 83),
    "grant": (AnsiStyle.BRIGHT_YELLOW, 66),
    "elevated": (AnsiStyle.BRIGHT_YELLOW, 93),
    "legacy": (AnsiStyle.YELLOW, 65),
    "unstable": (AnsiStyle.YELLOW, 72),
    "new": (AnsiStyle.BRIGHT_GREEN, 52),
    "owr": (AnsiStyle.RED, 64),
    "del": (AnsiStyle.RED, 82),
    "mv": (AnsiStyle.BRIGHT_GREEN, 47),
    "cp": (AnsiStyle.BRIGHT_GREEN, 46),
    "cached": (AnsiStyle.MAGENTA, 45),
    "stale": (AnsiStyle.YELLOW, 63),
    "auto": (AnsiStyle.BLUE, 33),
    "fresh": (AnsiStyle.GREEN, 44),
    "resume": (AnsiStyle.GREEN, 43),
    "offline": (AnsiStyle.YELLOW, 42),
    "watch": (AnsiStyle.BRIGHT_BLUE, 32),
    "bg": (AnsiStyle.BLUE, 31),
    "retry": (AnsiStyle.BRIGHT_MAGENTA, 41),
    "fallback": (AnsiStyle.BRIGHT_YELLOW, 62),
    "timeout": (AnsiStyle.BRIGHT_RED, 81),
    "abort": (AnsiStyle.BRIGHT_RED, 92),
}


class TestNativeBadgeTable:
    def test_has_exactly_the_documented_badges(_):
        assert set(_NATIVE_BADGES) == set(_EXPECTED)

    @pytest.mark.parametrize("label", sorted(_EXPECTED))
    def test_hue_and_priority(_, label):
        assert _NATIVE_BADGES[label] == _EXPECTED[label]

    def test_priorities_are_unique_positive_ints(_):
        priorities = [prio for _hue, prio in _NATIVE_BADGES.values()]
        assert len(set(priorities)) == len(priorities)
        assert all(isinstance(p, int) and p > 0 for p in priorities)
