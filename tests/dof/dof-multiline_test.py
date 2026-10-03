"""
dof-multiline_test.py

tests for per-line compression of multi-line messages in
`_DiffOnlyEngine._compress` in `kamilog`
"""

from kamilog.diff_only import _DiffOnlyEngine


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


def _compress_last(*messages, prefix_len=0):
    engine = _DiffOnlyEngine(
        _StubFormatter(prefix_len), threshold=len(messages) - 1
    )
    out = None
    for m in messages:
        out = engine.process(_StubRecord(m))
    return out


_A = "a" * 16 + "/bbb"


class TestPerLineCompression:
    def test_each_line_compresses_against_its_own_earlier_line(_):
        first = _A + "X\n" + _A + "P"
        second = _A + "Y\n" + _A + "Q"
        assert _compress_last(first, second) == (
            "<〃\t〃\t>/bbbY\n<〃\t〃\t>/bbbQ"
        )

    def test_line_count_is_preserved(_):
        first = "x\ny\nz"
        second = "x\ny\nz"
        assert _compress_last(first, second).count("\n") == 2

    def test_line_is_not_compared_with_other_line_index(_):
        first = _A + "X\nother"
        second = "other\n" + _A + "X"
        assert _compress_last(first, second) == second

    def test_only_first_line_carries_the_prefix(_):
        first = _A + "X\n" + _A + "P"
        second = _A + "Y\n" + _A + "Q"
        # line 1 starts at col 3; line 2 still starts at col 0
        assert _compress_last(first, second, prefix_len=3) == (
            "<〃\t><〃\t><〃> /bbbY\n<〃\t〃\t>/bbbQ"
        )

    def test_first_line_leader_only_on_first_line(_):
        first = _A + "X\n" + _A + "P"
        second = _A + "Y\n" + _A + "Q"
        # prefix 5: line 1 gets a bare-tab leader, line 2 does not
        out = _compress_last(first, second, prefix_len=5)
        line1, line2 = out.split("\n")
        assert line1.startswith("\t")
        assert not line2.startswith("\t")

    def test_later_line_matches_col_zero_alignment(_):
        first = "0\n" + _A + "X"
        second = "1\n" + _A + "Y"
        assert _compress_last(first, second).split("\n")[1] == (
            "<〃\t〃\t>/bbbY"
        )

    def test_extra_line_in_new_message_stays_verbatim(_):
        first = _A + "X"
        second = _A + "Y\nnew line"
        assert _compress_last(first, second) == "<〃\t〃\t>/bbbY\nnew line"

    def test_fewer_lines_in_new_message_does_not_crash(_):
        first = _A + "X\n" + _A + "P"
        second = _A + "Y"
        assert _compress_last(first, second) == "<〃\t〃\t>/bbbY"

    def test_empty_lines_survive(_):
        first = "a\n\nb"
        second = "a\n\nb"
        assert _compress_last(first, second) == "a\n\nb"

    def test_single_line_behavior_is_unchanged(_):
        first = _A + "X"
        second = _A + "Y"
        assert _compress_last(first, second) == "<〃\t〃\t>/bbbY"
