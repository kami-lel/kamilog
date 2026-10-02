"""
lf-badge-color_test.py

tests for badge coloring in `AnsiRenderer.color_badge` and
`_LogFormatEngine.build_line` in `kamilog.py`
"""

import logging

import pytest

from kamilog.kamilog import (
    _NATIVE_BADGES,
    AnsiRenderer,
    _LogFormatEngine,
)


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


def _renderer(is_tty=True):
    return AnsiRenderer(_FakeStream(is_tty))


def _record(badges):
    record = logging.LogRecord("x", 25, "path", 1, "m", (), None)
    record.badges = badges
    return record


class TestColorBadge:
    @pytest.mark.parametrize("label", sorted(_NATIVE_BADGES))
    def test_native_badge_uses_its_hue(_, label):
        renderer = _renderer()
        hue = _NATIVE_BADGES[label][0]
        assert renderer.color_badge(label, label) == renderer.color(
            label, hue
        )

    def test_dry_is_bright_yellow(_):
        assert _renderer().color_badge("dry", "dry") == "\033[93mdry\033[0m"

    def test_custom_badge_is_magenta(_):
        assert _renderer().color_badge("deploy", "deploy") == (
            "\033[35mdeploy\033[0m"
        )

    def test_plain_when_color_disabled(_):
        assert _renderer(False).color_badge("dry", "dry") == "dry"


def _build_line(badges, is_tty=True):
    engine = _LogFormatEngine(_renderer(is_tty), datefmt=None)
    return engine.build_line(_record(badges))


class TestBuildLineBadgeColor:
    def test_each_badge_colored_separators_plain(_):
        line = _build_line(("dry", "x"))
        colored = "\033[93mdry\033[0m \033[35mx\033[0m"
        badge_seg = "{}\t".format(colored)
        assert badge_seg in line
        assert line.index("DONE") < line.index(badge_seg)

    def test_plain_output_has_bare_labels(_):
        line = _build_line(("dry", "yes"), is_tty=False)
        assert "\033" not in line
        assert line.startswith("DONE  dry yes\t")

    def test_no_badges_adds_no_tabs(_):
        assert "\t" not in _build_line((), is_tty=False)
