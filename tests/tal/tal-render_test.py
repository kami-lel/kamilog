"""
tal-render_test.py

tests for `_TabAlignedLine.render` in `kamilog.py`
"""

from kamilog.kamilog import _TabAlignedLine


class TestRenderWithoutPrefix:
    def test_default_kwargs_join_blocks(_):
        line = _TabAlignedLine.parse("abcdefgh12345")
        assert line.render() == "abcdefgh12345"

    def test_insert_prefix_false_ignores_offset(_):
        line = _TabAlignedLine.parse("abcdefgh12345", start_offset=3)
        assert line.render(insert_prefix=False) == "abcdefgh12345"

    def test_roundtrip_matches_original_line(_):
        original = "abcdefgh12345678xyz"
        line = _TabAlignedLine.parse(original)
        assert line.render() == original


class TestRenderWithPrefix:
    def test_default_prefix_symbol_is_space(_):
        line = _TabAlignedLine.parse("abc", start_offset=3)
        assert line.render(insert_prefix=True) == "   abc"

    def test_custom_prefix_symbol(_):
        line = _TabAlignedLine.parse("abc", start_offset=3)
        assert line.render(
            insert_prefix=True, prefix_symbol="-"
        ) == "---abc"

    def test_zero_offset_adds_no_prefix(_):
        line = _TabAlignedLine.parse("abc", start_offset=0)
        assert line.render(insert_prefix=True) == "abc"

    def test_prefix_length_matches_start_offset(_):
        line = _TabAlignedLine.parse("abc", start_offset=5)
        result = line.render(insert_prefix=True, prefix_symbol="*")
        assert result == "*****abc"

    def test_multi_char_prefix_symbol_repeats_whole(_):
        line = _TabAlignedLine.parse("abc", start_offset=2)
        result = line.render(insert_prefix=True, prefix_symbol="ab")
        assert result == "abababc"
