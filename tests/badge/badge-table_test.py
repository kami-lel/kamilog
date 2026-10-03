"""
badge-table_test.py

tests for `_NATIVE_BADGES` in `kamilog`
"""

import pytest

from kamilog import AnsiStyle
from kamilog.badges import _NATIVE_BADGES

_EXPECTED = {
    "dry": (AnsiStyle.BRIGHT_YELLOW, 73),
    "chk": (AnsiStyle.YELLOW, 68),
    "mock": (AnsiStyle.YELLOW, 67),
    "sandbox": (AnsiStyle.GREEN, 53),
    "force": (AnsiStyle.RED, 84),
    "undo": (AnsiStyle.RED, 83),
    "grant": (AnsiStyle.YELLOW, 66),
    "elevated": (AnsiStyle.BRIGHT_RED, 93),
    "legacy": (AnsiStyle.YELLOW, 65),
    "unstable": (AnsiStyle.BRIGHT_YELLOW, 72),
    "new": (AnsiStyle.GREEN, 52),
    "owr": (AnsiStyle.YELLOW, 64),
    "del": (AnsiStyle.RED, 82),
    "mv": (AnsiStyle.CYAN, 47),
    "cp": (AnsiStyle.CYAN, 46),
    "cached": (AnsiStyle.CYAN, 45),
    "stale": (AnsiStyle.YELLOW, 63),
    "auto": (AnsiStyle.BLUE, 33),
    "fresh": (AnsiStyle.CYAN, 44),
    "resume": (AnsiStyle.CYAN, 43),
    "offline": (AnsiStyle.CYAN, 42),
    "watch": (AnsiStyle.BLUE, 32),
    "bg": (AnsiStyle.BLUE, 31),
    "retry": (AnsiStyle.CYAN, 41),
    "fallback": (AnsiStyle.YELLOW, 62),
    "skip": (AnsiStyle.YELLOW, 61),
    "timeout": (AnsiStyle.RED, 81),
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
