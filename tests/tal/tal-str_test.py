"""
tal-str_test.py

tests for `_TabAlignedLine.__str__` in `kamilog.py`
"""

from kamilog.kamilog import _TabAlignedLine


class TestStr:
    def test_matches_render_default(_):
        line = _TabAlignedLine.parse("abcdefgh12345", start_offset=3)
        assert str(line) == line.render()

    def test_ignores_offset_like_render_default(_):
        line = _TabAlignedLine.parse("abc", start_offset=4)
        assert str(line) == "abc"

    def test_roundtrips_original_line(_):
        original = "abcdefgh12345678xyz"
        line = _TabAlignedLine.parse(original)
        assert str(line) == original
