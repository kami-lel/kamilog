"""
dof-badge-interaction_test.py

end-to-end tests of badges with diff-only ditto alignment, through
`getLogger` and a file handler, in `kamilog`
"""

import logging
import uuid

import pytest

from kamilog import DATEFMT_TIME, getLogger

_TAB = 8
_TAIL = "/bbb"
_BADGE_SETS = [
    (),
    ("dry",),
    ("dry", "yes"),
    ("force", "dry", "retry", "auto"),  # given order
    ("elevated", "deploy-staging-env"),
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
    logger.set_persistent_badges(badges)
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
            assert lines[3].index("{}\t".format(label)) < marker

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
        assert "dry\t" in lines[3]
        ref = _tail_col(lines[1], _TAIL + "X")
        assert _tail_col(lines[3], _TAIL + "Y") == ref


def _split_records(lines, n_records, n_lines):
    """regroup physical file lines into one list per record"""
    assert len(lines) == n_records * n_lines
    return [
        lines[i * n_lines : (i + 1) * n_lines] for i in range(n_records)
    ]


class TestBadgedMultiLineMessage:
    @pytest.mark.parametrize("datefmt", [None, DATEFMT_TIME])
    @pytest.mark.parametrize("badges", _BADGE_SETS)
    def test_each_line_keeps_its_own_column(_, tmp_path, badges, datefmt):
        line1 = "a" * 20 + _TAIL
        line2 = "b" * 40 + _TAIL
        messages = [
            "{}X\n{}P".format(line1, line2),
        ] * 3 + ["{}Y\n{}Q".format(line1, line2)]
        lines = _log_lines(
            tmp_path, messages, badges=badges, datefmt=datefmt, name_len=1
        )
        first, *_mid, last = _split_records(lines, 4, 2)
        assert _display_cols(first[0]) <= 100  # both lines stay short
        # line 1 carries the badged prefix, line 2 starts at column 0
        assert _tail_col(last[0], _TAIL + "Y") == _tail_col(
            first[0], _TAIL + "X"
        )
        assert _tail_col(last[1], _TAIL + "Q") == _tail_col(
            first[1], _TAIL + "P"
        )
        assert "〃" in last[0] and "〃" in last[1]

    def test_second_line_has_no_prefix_or_badge_text(_, tmp_path):
        body = "a" * 20 + _TAIL
        messages = ["{}X\n{}P".format(body, body)] * 3
        messages.append("{}Y\n{}Q".format(body, body))
        lines = _log_lines(tmp_path, messages, badges=("dry", "yes"))
        last = _split_records(lines, 4, 2)[-1]
        assert "dry" not in last[1]
        assert last[1].startswith("〃")

    def test_line_count_change_does_not_crash_or_misalign(_, tmp_path):
        body = "a" * 20 + _TAIL
        messages = [body + "X"] * 3 + ["{}Y\nextra".format(body)]
        lines = _log_lines(tmp_path, messages, badges=("dry",))
        assert len(lines) == 5
        assert lines[4] == "extra"
        assert _tail_col(lines[3], _TAIL + "Y") == _tail_col(
            lines[0], _TAIL + "X"
        )


class TestBadgedLongMultiLineMessage:
    def _long_records(_, tmp_path, badges, datefmt):
        short = "a" * 20 + _TAIL
        long = "c" * 120 + _TAIL
        messages = [
            "{}X\n{}P".format(short, long),
        ] * 3 + ["{}Y\n{}Q".format(short, long)]
        lines = _log_lines(
            tmp_path, messages, badges=badges, datefmt=datefmt
        )
        return _split_records(lines, 4, 2)

    @pytest.mark.parametrize("badges", _BADGE_SETS)
    def test_short_line_keeps_tabs_long_line_uses_spaces(_, tmp_path, badges):
        first, *_mid, last = TestBadgedLongMultiLineMessage._long_records(
            _, tmp_path, badges, None
        )
        assert _display_cols(first[1]) > 100
        assert "〃\t" in last[0]
        assert "〃\t" not in last[1]
        assert last[1].startswith("〃 〃 ")
        assert "\t" not in last[1]

    @pytest.mark.parametrize("badges", _BADGE_SETS)
    def test_long_line_tail_is_kept_intact(_, tmp_path, badges):
        *_head, last = TestBadgedLongMultiLineMessage._long_records(
            _, tmp_path, badges, DATEFMT_TIME
        )
        assert last[1].endswith(_TAIL + "Q")
        assert last[0].endswith(_TAIL + "Y")

    def test_badges_can_push_only_line_one_over_the_limit(_, tmp_path):
        # 70 columns of message: short at col 0, long behind 40+ prefix
        body = "d" * 66 + _TAIL
        badges = ("elevated", "deploy-staging-env")
        messages = ["{}X\n{}P".format(body, body)] * 3
        messages.append("{}Y\n{}Q".format(body, body))
        lines = _log_lines(tmp_path, messages, badges=badges)
        first, *_mid, last = _split_records(lines, 4, 2)
        assert _display_cols(first[0]) > 100
        assert _display_cols(first[1]) <= 100
        assert "〃\t" not in last[0]  # line 1: spaced
        assert "〃\t" in last[1]  # line 2: still tab aligned
