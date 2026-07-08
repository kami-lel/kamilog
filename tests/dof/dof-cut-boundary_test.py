"""
dof-cut-boundary_test.py

tests for `_DiffOnlyEngine._find_cut` and `_is_word_char` in `kamilog.py`
"""

from kamilog.kamilog import _DiffOnlyEngine

_engine = _DiffOnlyEngine.__new__(_DiffOnlyEngine)


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


class TestFindCutFallback:
    def test_no_boundary_falls_back_to_tab_span_floor(_):
        message = "a" * 40
        cut = _engine._find_cut(message, 0, 40, prefix_len=10)
        assert cut == 22

    def test_boundary_before_floor_is_ignored(_):
        message = list("a" * 40)
        message[21] = "/"
        cut = _engine._find_cut("".join(message), 0, 40, prefix_len=10)
        assert cut == 22


class TestFindCutBoundaryWithinSpan:
    def test_boundary_within_span_is_returned(_):
        message = list("a" * 40)
        message[30] = "/"
        cut = _engine._find_cut("".join(message), 0, 40, prefix_len=10)
        assert cut == 30

    def test_nearest_boundary_to_run_end_wins(_):
        message = list("a" * 40)
        message[25] = "/"
        message[35] = ":"
        cut = _engine._find_cut("".join(message), 0, 40, prefix_len=10)
        assert cut == 35
