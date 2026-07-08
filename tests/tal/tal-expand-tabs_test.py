"""
tal-expand-tabs_test.py

tests for the literal "\\t" expansion built into `_TabAlignedLine.parse`
in `kamilog.py`
"""

from kamilog.kamilog import _TabAlignedLine


class TestExpandTabsNoOffset:
    def test_lone_tab_expands_to_full_block(_):
        result = _TabAlignedLine.parse("\t")
        assert result.render() == " " * 8

    def test_tab_after_short_prefix_fills_to_next_stop(_):
        result = _TabAlignedLine.parse("ab\tcd")
        assert result.render() == "ab      cd"

    def test_tab_at_stop_boundary_advances_a_full_block(_):
        # "abcdefgh" already lands exactly on a tab stop (8 chars), so
        # the following tab must add a full block, not zero
        result = _TabAlignedLine.parse("abcdefgh\tx")
        assert result.render() == "abcdefgh" + " " * 8 + "x"

    def test_consecutive_tabs_each_advance_a_full_block(_):
        result = _TabAlignedLine.parse("\t\t")
        assert result.render() == " " * 16

    def test_tab_at_end_of_line(_):
        result = _TabAlignedLine.parse("abc\t")
        assert result.render() == "abc" + " " * 5

    def test_no_tabs_is_unaffected(_):
        result = _TabAlignedLine.parse("abcdefgh12345")
        assert result.render() == "abcdefgh12345"


class TestExpandTabsWithOffset:
    def test_offset_shortens_first_tab_stop(_):
        result = _TabAlignedLine.parse("\t", start_offset=3)
        assert result.render() == " " * 5

    def test_offset_at_stop_boundary_still_advances_full_block(_):
        result = _TabAlignedLine.parse("\t", start_offset=8)
        assert result.render() == " " * 8

    def test_offset_larger_than_tab_size_wraps_to_remainder(_):
        result = _TabAlignedLine.parse("\t", start_offset=11)
        assert result.render() == " " * 5

    def test_text_then_tab_with_offset(_):
        # start_offset=5: "a" -> col 6, tab fills to col 8 (2 spaces)
        result = _TabAlignedLine.parse("a\tb", start_offset=5)
        assert result.render() == "a" + " " * 2 + "b"

    def test_multiple_tabs_with_offset(_):
        # start_offset=5: 'a'->6, tab->8 (2sp), 'b'->9, tab->16 (7sp)
        result = _TabAlignedLine.parse("a\tb\tc", start_offset=5)
        assert result.render() == "a" + " " * 2 + "b" + " " * 7 + "c"


class TestExpandTabsBlockSplitting:
    def test_expanded_blocks_are_tab_size_except_last(_):
        result = _TabAlignedLine.parse("ab\tcd\tef")
        for block in result[:-1]:
            assert len(block) == _TabAlignedLine.TAB_SIZE

    def test_block_count_matches_expanded_length(_):
        result = _TabAlignedLine.parse("\t\t\tabc")
        total = sum(len(block) for block in result)
        assert total == len(result.render())

    def test_offset_still_shortens_first_block_after_expansion(_):
        result = _TabAlignedLine.parse("\tabc", start_offset=3)
        assert len(result[0]) == 5

    def test_render_round_trips_through_blocks(_):
        result = _TabAlignedLine.parse("row\tid=00{}\tstatus=ok".format(1))
        assert "".join(result) == result.render()
