"""
dof-cut-boundary_test.py

tests for `_DiffOnlyEngine._find_block_cut` and `_is_word_char` in
`kamilog.py`
"""

from kamilog.kamilog import _DiffOnlyEngine, _TabAlignedLine

_engine = _DiffOnlyEngine.__new__(_DiffOnlyEngine)


def _find_block_cut(message, run_bs, run_be):
    starts = _TabAlignedLine.parse(message, start_offset=0).block_starts()
    return _engine._find_block_cut(message, starts, run_bs, run_be)


class TestIsWordChar:
    def test_lowercase_letter_is_word_char(_):
        assert _engine._is_word_char("a") is True

    def test_uppercase_letter_is_word_char(_):
        assert _engine._is_word_char("Z") is True

    def test_digit_is_word_char(_):
        assert _engine._is_word_char("9") is True

    def test_underscore_is_word_char(_):
        assert _engine._is_word_char("_") is True

    def test_hyphen_is_word_char(_):
        assert _engine._is_word_char("-") is True

    def test_slash_is_not_word_char(_):
        assert _engine._is_word_char("/") is False

    def test_space_is_not_word_char(_):
        assert _engine._is_word_char(" ") is False

    def test_colon_is_not_word_char(_):
        assert _engine._is_word_char(":") is False


class TestFindBlockCutRunEndsAtMessageEnd:
    def test_full_run_is_safe_when_nothing_follows(_):
        # 5 full 8-char blocks, message ends exactly on a tab stop
        message = "a" * 40
        assert _find_block_cut(message, 0, 5) == 5


class TestFindBlockCutFallback:
    def test_no_safe_boundary_falls_back_to_span_floor(_):
        # blocks 0-4 are word chars, and the next block ('Z') is too
        message = "a" * 40 + "Z"
        assert _find_block_cut(message, 0, 5) == 3


class TestFindBlockCutBoundaryWithinSpan:
    def test_boundary_one_block_back_is_used(_):
        message = list("a" * 40 + "Z")
        message[32] = "/"  # boundary char at the start of block index 4
        assert _find_block_cut("".join(message), 0, 5) == 4

    def test_boundary_outside_span_is_ignored(_):
        message = list("a" * 40 + "Z")
        message[24] = "/"  # boundary at block index 3, outside the span
        assert _find_block_cut("".join(message), 0, 5) == 3

    def test_nearer_boundary_wins_over_farther_one(_):
        message = list("a" * 40 + "Z")
        message[24] = "/"  # block index 3, outside span
        message[32] = ":"  # block index 4, within span
        assert _find_block_cut("".join(message), 0, 5) == 4
