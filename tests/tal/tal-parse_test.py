"""
tal-parse_test.py

tests for `_TabAlignedLine.parse` in `kamilog.py`
"""

from kamilog.kamilog import _TabAlignedLine


class TestParseNoOffset:
    def test_empty_line(_):
        result = _TabAlignedLine.parse("")
        assert list(result) == [""]

    def test_shorter_than_tab_size(_):
        result = _TabAlignedLine.parse("abc")
        assert list(result) == ["abc"]

    def test_exact_tab_size(_):
        result = _TabAlignedLine.parse("abcdefgh")
        assert list(result) == ["abcdefgh"]

    def test_exact_multiple_of_tab_size(_):
        result = _TabAlignedLine.parse("abcdefgh12345678")
        assert list(result) == ["abcdefgh", "12345678"]

    def test_non_multiple_of_tab_size(_):
        result = _TabAlignedLine.parse("abcdefgh12345")
        assert list(result) == ["abcdefgh", "12345"]

    def test_default_start_offset_is_zero(_):
        result = _TabAlignedLine.parse("abc")
        assert result.start_offset == 0


class TestParseWithOffset:
    def test_offset_shortens_first_block(_):
        result = _TabAlignedLine.parse("abcdefgh12345", start_offset=3)
        assert list(result) == ["abcde", "fgh12345"]

    def test_offset_equal_to_tab_size_is_full_first_block(_):
        result = _TabAlignedLine.parse("abcdefgh12345678", start_offset=8)
        assert list(result) == ["abcdefgh", "12345678"]

    def test_offset_larger_than_tab_size_wraps(_):
        result = _TabAlignedLine.parse("abcdefgh12345", start_offset=11)
        assert list(result) == ["abcde", "fgh12345"]

    def test_offset_longer_than_line(_):
        result = _TabAlignedLine.parse("ab", start_offset=3)
        assert list(result) == ["ab"]

    def test_stores_start_offset(_):
        result = _TabAlignedLine.parse("abcdefgh", start_offset=5)
        assert result.start_offset == 5


class TestParseReturnType:
    def test_returns_instance_of_class(_):
        result = _TabAlignedLine.parse("abc")
        assert isinstance(result, _TabAlignedLine)

    def test_result_is_a_list(_):
        result = _TabAlignedLine.parse("abc")
        assert isinstance(result, list)

    def test_tab_size_is_eight(_):
        assert _TabAlignedLine.TAB_SIZE == 8
