"""
dof-badge-interaction_test.py

end-to-end tests of badges with diff-only ditto alignment, through
`getLogger` and a file handler, in `kamilog.py`
"""

import logging
import uuid

import pytest

from kamilog.kamilog import DATEFMT_TIME, getLogger

_TAB = 8
_TAIL = "/bbb"
_BADGE_SETS = [
    (),
    ("dry",),
    ("dry", "yes"),
    ("force", "dry", "retries", "auto"),  # priority order
    ("unsafe", "deploy-staging-env"),
]


def _display_cols(text):
    """rendered width of ``text``: tabs to stops, ditto marker 2 wide"""
    col = 0
    for ch in text:
        if ch == "\t":
            col += _TAB - col % _TAB
        elif ch == "〃":
            col += 2
        else:
            col += 1
    return col


def _tail_col(line, tail):
    """rendered column where the last ``tail`` begins in ``line``"""
    return _display_cols(line[: line.rindex(tail)])


def _log_lines(tmp_path, messages, *, badges=(), name_len=32, **kwargs):
    """log ``messages`` through a file-only logger, return file lines"""
    path = tmp_path / "out.log"
    logger = getLogger(
        uuid.uuid4().hex[:name_len],  # fresh logger: no shared history
        filename=str(path),
        disable_console=True,
        **kwargs,
    )
    logger.setLevel(logging.DEBUG)
    logger.set_badges(badges)
    for message in messages:
        logger.info(message)
    for handler in logger.handlers:
        handler.flush()
    return path.read_text().split("\n")[:-1]


class TestDittoAlignmentUnderBadges:
    @pytest.mark.parametrize("datefmt", [None, DATEFMT_TIME])
    @pytest.mark.parametrize("name_len", [1, 20])
    @pytest.mark.parametrize("badges", _BADGE_SETS)
    def test_tail_lands_on_its_uncompressed_column(
        _, tmp_path, badges, name_len, datefmt
    ):
        body = "a" * 20 + _TAIL  # short even under the widest prefix
        messages = [body + "X"] * 3 + [body + "Y"]
        lines = _log_lines(
            tmp_path,
            messages,
            badges=badges,
            name_len=name_len,
            datefmt=datefmt,
        )
        assert len(lines) == 4
        assert _display_cols(lines[0]) <= 100
        assert "〃" in lines[3]
        assert _tail_col(lines[3], _TAIL + "Y") == _tail_col(
            lines[0], _TAIL + "X"
        )

    @pytest.mark.parametrize("badges", _BADGE_SETS)
    def test_dittos_start_at_or_after_the_message_column(_, tmp_path, badges):
        body = "a" * 20 + _TAIL
        messages = [body + "X"] * 3 + [body + "Y"]
        lines = _log_lines(tmp_path, messages, badges=badges)
        message_col = _display_cols(lines[0][: lines[0].index("a" * 20)])
        marker = lines[3].index("〃")
        assert _display_cols(lines[3][:marker]) >= message_col
        if badges:
            label = " ".join(badges)
            assert lines[3].index("\t{}\t".format(label)) < marker

    def test_no_badges_prints_no_added_tabs_in_the_prefix(_, tmp_path):
        lines = _log_lines(tmp_path, ["hello"], badges=())
        assert "\t" not in lines[0]

    def test_per_call_badges_align_too(_, tmp_path):
        path = tmp_path / "out.log"
        logger = getLogger(
            uuid.uuid4().hex,
            filename=str(path),
            disable_console=True,
            datefmt=None,
        )
        logger.setLevel(logging.DEBUG)
        body = "a" * 20 + _TAIL
        for suffix in ("X", "X", "X", "Y"):
            logger.info(body + suffix, badges=["dry", "yes"])
        for handler in logger.handlers:
            handler.flush()
        lines = path.read_text().split("\n")[:-1]
        assert _tail_col(lines[3], _TAIL + "Y") == _tail_col(
            lines[0], _TAIL + "X"
        )

    def test_badges_changing_between_records_keep_alignment(_, tmp_path):
        path = tmp_path / "out.log"
        logger = getLogger(
            uuid.uuid4().hex,
            filename=str(path),
            disable_console=True,
            datefmt=None,
        )
        logger.setLevel(logging.DEBUG)
        body = "a" * 20 + _TAIL
        logger.info(body + "X")
        logger.info(body + "X", badges="dry")
        logger.info(body + "X", badges=["dry", "yes", "force"])
        logger.info(body + "Y", badges="dry")
        for handler in logger.handlers:
            handler.flush()
        lines = path.read_text().split("\n")[:-1]
        assert "〃" in lines[3]
        # the line's own prefix decides the column: 4th line has one badge
        with_badge = "\tdry\t"
        assert with_badge in lines[3]
        ref = _tail_col(lines[1], _TAIL + "X")
        assert _tail_col(lines[3], _TAIL + "Y") == ref
