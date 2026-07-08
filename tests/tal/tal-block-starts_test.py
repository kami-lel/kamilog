"""
tal-block-starts_test.py

tests for `_TabAlignedLine.block_starts` in `kamilog.py`
"""

from kamilog.kamilog import _TabAlignedLine


class TestBlockStartsNoOffset:
    def test_empty_line_has_single_zero_start(_):
        line = _TabAlignedLine.parse("")
        assert line.block_starts() == [0]

    def test_single_block_starts_at_zero(_):
        line = _TabAlignedLine.parse("abc")
        assert line.block_starts() == [0]

    def test_two_full_blocks(_):
        line = _TabAlignedLine.parse("abcdefgh12345678")
        assert line.block_starts() == [0, 8]

    def test_full_block_plus_remainder(_):
        line = _TabAlignedLine.parse("abcdefgh12345")
        assert line.block_starts() == [0, 8]


class TestBlockStartsWithOffset:
    def test_short_first_block_shifts_second_start(_):
        line = _TabAlignedLine.parse("abcdefgh12345", start_offset=3)
        assert line.block_starts() == [0, 5]

    def test_offset_equal_to_tab_size_has_full_first_block(_):
        line = _TabAlignedLine.parse("abcdefgh12345678", start_offset=8)
        assert line.block_starts() == [0, 8]

    def test_matches_cumulative_block_lengths(_):
        line = _TabAlignedLine.parse("abcdefgh12345678xyz", start_offset=3)
        starts = line.block_starts()
        expected = []
        pos = 0
        for block in line:
            expected.append(pos)
            pos += len(block)
        assert starts == expected
