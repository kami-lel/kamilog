"""
badge-table_test.py

tests for `_NATIVE_BADGES` in `kamilog`
"""

import pytest

from kamilog import AnsiStyle
from kamilog.badges import _NATIVE_BADGES

_EXPECTED = {
    "dry": (AnsiStyle.BRIGHT_YELLOW, 45),
    "chk": (AnsiStyle.YELLOW, 44),
    "mock": (AnsiStyle.YELLOW, 43),
    "sbx": (AnsiStyle.GREEN, 33),
    "force": (AnsiStyle.RED, 52),
    "undo": (AnsiStyle.RED, 51),
    "unsafe": (AnsiStyle.BRIGHT_RED, 53),
    "yes": (AnsiStyle.YELLOW, 42),
    "auto": (AnsiStyle.BLUE, 13),
    "strict": (AnsiStyle.GREEN, 32),
    "keep": (AnsiStyle.YELLOW, 41),
    "fast": (AnsiStyle.GREEN, 31),
    "retries": (AnsiStyle.CYAN, 25),
    "resm": (AnsiStyle.CYAN, 24),
    "new": (AnsiStyle.CYAN, 23),
    "offl": (AnsiStyle.CYAN, 22),
    "incr": (AnsiStyle.CYAN, 21),
    "watch": (AnsiStyle.BLUE, 12),
    "bg": (AnsiStyle.BLUE, 11),
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
