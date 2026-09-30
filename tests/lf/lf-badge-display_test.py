"""
lf-badge-display_test.py

tests for the badge segment of `_LogFormatEngine.build_line` in `kamilog.py`
"""

import logging

from kamilog.kamilog import DATEFMT_TIME, _LogFormatEngine


class _StubPalette:
    def color_grey(self, text):
        return text

    def color_level(self, text, levelno):
        return text

    def color_badge(self, text, badge):
        return text


def _make_record(name="mymodule", badges=None, levelno=25):
    msg = "wrote a.txt"
    record = logging.LogRecord(name, levelno, "path", 1, msg, (), None)
    if badges is not None:
        record.badges = badges
    return record


def _engine(datefmt=None):
    return _LogFormatEngine(_StubPalette(), datefmt=datefmt)


class TestBadgeSegment:
    def test_no_badge_attr_is_unchanged(_):
        line = _engine().build_line(_make_record())
        assert line == "DONE  mymodule: wrote a.txt"

    def test_empty_badges_is_unchanged(_):
        line = _engine().build_line(_make_record(badges=()))
        assert line == "DONE  mymodule: wrote a.txt"
        assert "\t" not in line

    def test_one_badge_before_the_level(_):
        line = _engine().build_line(_make_record(badges=("dry",)))
        assert line == "dry\tDONE  mymodule: wrote a.txt"

    def test_several_badges_space_separated(_):
        line = _engine().build_line(_make_record(badges=("dry", "yes")))
        assert line == "dry yes\tDONE  mymodule: wrote a.txt"

    def test_badges_follow_the_timestamp(_):
        record = _make_record(badges=("dry", "yes"))
        line = _engine(DATEFMT_TIME).build_line(record)
        head, rest = line.split(" ", 1)
        assert len(head) == 8
        assert rest == "dry yes\tDONE  mymodule: wrote a.txt"

    def test_root_logger_keeps_bare_colon(_):
        line = _engine().build_line(_make_record("root", ("dry",)))
        assert line == "dry\tDONE : wrote a.txt"

    def test_custom_badge_printed_bare(_):
        line = _engine().build_line(_make_record(badges=("deploy",)))
        assert line.startswith("deploy\tDONE")
