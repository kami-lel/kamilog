"""
dof-marker-render_test.py

tests for `_DiffOnlyEngine._compress` marker rendering in `kamilog.py`
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


class TestExactBlockMultiple:
    def test_padding_zero_and_gap_zero_emit_bare_markers(_):
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        assert _compress_second(a, b) == "<〃\t〃\t>/bbbY"


class TestShortLeaderBecomesBareTab:
    def test_padding_below_minimum_emits_bare_tab_leader(_):
        a = "abc12" + "a" * 11 + "/ccc" + "X"
        b = "xyz34" + "a" * 11 + "/ccc" + "Y"
        assert _compress_second(a, b) == "xyz34\t<〃\t>/cccY"


class TestLongLeaderEarnsMarker:
    def test_padding_at_minimum_emits_colored_leader_marker(_):
        a = "abcd" + "a" * 12 + "/ddd" + "X"
        b = "wxyz" + "a" * 12 + "/ddd" + "Y"
        assert _compress_second(a, b) == "wxyz<〃\t><〃\t>/dddY"


class TestPartialBlockGap:
    def test_gap_at_or_above_marker_width_adds_marker_and_spaces(_):
        a = "a" * 11 + "/eee" + "X"
        b = "a" * 11 + "/eee" + "Y"
        assert _compress_second(a, b) == "<〃\t><〃> /eeeY"

    def test_gap_below_marker_width_adds_spaces_only(_):
        a = "a" * 9 + "/ff" + "X"
        b = "a" * 9 + "/ff" + "Y"
        assert _compress_second(a, b) == "<〃\t> /ffY"


class TestUnreplaceableShortRun:
    def test_run_shorter_than_one_block_stays_literal(_):
        a = "abc"
        b = "abd"
        assert _compress_second(a, b) == "abd"
