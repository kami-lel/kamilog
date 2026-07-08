"""
dof-marker-render_test.py

tests for `_DiffOnlyEngine._compress` block-level marker rendering in
`kamilog.py`
"""

from kamilog.kamilog import _DiffOnlyEngine


class _StubEngine:
    def __init__(self, prefix_len):
        self._prefix_len = prefix_len

    def count_prefix_chars(self, record):
        return self._prefix_len


class _StubPalette:
    def color_grey(self, text):
        return "<{}>".format(text)


class _StubFormatter:
    def __init__(self, prefix_len=0):
        self.engine = _StubEngine(prefix_len)
        self.palette = _StubPalette()


class _StubRecord:
    def __init__(self, message):
        self._message = message

    def getMessage(self):
        return self._message


def _compress_second(first, second, *, prefix_len=0):
    engine = _DiffOnlyEngine(_StubFormatter(prefix_len), threshold=1)
    engine.process(_StubRecord(first))
    return engine.process(_StubRecord(second))


class TestWholeBlockReplacement:
    def test_two_full_common_blocks_each_get_their_own_marker(_):
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        assert _compress_second(a, b) == "<〃\t><〃\t>/bbbY"

    def test_run_reaching_message_end_replaces_every_full_block(_):
        a = "a" * 16
        b = "a" * 16
        assert _compress_second(a, b) == "<〃\t><〃\t>"


class TestSubBlockRunsStayLiteral:
    def test_run_shorter_than_one_block_is_never_compressed(_):
        assert _compress_second("abc", "abd") == "abd"

    def test_block_straddling_a_divergence_stays_fully_literal(_):
        # only the last 11 of the first 16 chars are common, so the
        # block containing the divergence can never be a whole-block
        # candidate, even though most of it matches
        a = "abc12" + "a" * 11 + "/ccc" + "X"
        b = "xyz34" + "a" * 11 + "/ccc" + "Y"
        assert _compress_second(a, b) == "xyz34aaa<〃\t>/cccY"


class TestFallbackWhenNoSafeBoundary:
    def test_falls_back_to_span_floor_leaving_trailing_blocks_literal(_):
        a = "a" * 40 + "X"
        b = "a" * 40 + "Y"
        assert (
            _compress_second(a, b)
            == "<〃\t><〃\t><〃\t>aaaaaaaaaaaaaaaaY"
        )


class TestBoundaryWithinSpanStopsCompression:
    def test_safe_boundary_one_block_back_is_used(_):
        a = "a" * 16 + ":" + "a" * 7 + "X"
        b = "a" * 16 + ":" + "a" * 7 + "Y"
        assert _compress_second(a, b) == "<〃\t><〃\t>:aaaaaaaY"


class TestPrefixOffsetShiftsBlockBoundaries:
    def test_boundary_inside_a_block_is_not_detected(_):
        # the safe '/' sits at the end of the third block rather than
        # at a block boundary, so the coarser block-level scan can't
        # see it and the whole run stays literal
        a = "a" * 20 + "/eee" + "X"
        b = "a" * 20 + "/eee" + "Y"
        assert _compress_second(a, b, prefix_len=3) == (
            "aaaaaaaaaaaaaaaaaaaa/eeeY"
        )
