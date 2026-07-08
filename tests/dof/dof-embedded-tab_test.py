"""
dof-embedded-tab_test.py

tests for `_DiffOnlyEngine._compress` when message content already
contains a literal "\\t" in `kamilog.py`; `_TabAlignedLine.parse`
expands such tabs into spaces before splitting into blocks, so
compression must stay correct instead of drifting off tab stops
"""

import pytest

from kamilog.kamilog import _DiffOnlyEngine


class _StubEngine:
    def __init__(self, prefix_len=0):
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


class TestWarmupPreservesLiteralTabs:
    def test_message_within_threshold_keeps_raw_tab_chars(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=3)
        message = "row\tsensor=cpu\tid=001\tstatus=ok"
        assert engine.process(_StubRecord(message)) == message


class TestEmbeddedTabInCommonPrefix:
    def test_common_run_spanning_a_tab_compresses(_):
        a = "row\tsensor=cpu\tid=001\tstatus=ok"
        b = "row\tsensor=cpu\tid=002\tstatus=ok"
        assert (
            _compress_second(a, b) == "<〃\t〃\t〃\t><〃>=002\tstatus=ok"
        )

    def test_divergent_field_after_tab_stays_literal(_):
        a = "row\tsensor=cpu\tid=001\tstatus=ok"
        b = "row\tsensor=cpu\tid=002\tstatus=ok"
        result = _compress_second(a, b)
        assert result.endswith("=002\tstatus=ok")

    def test_literal_tab_before_status_field_is_preserved(_):
        a = "row\tsensor=cpu\tid=001\tstatus=ok"
        b = "row\tsensor=cpu\tid=002\tstatus=ok"
        result = _compress_second(a, b)
        # the marker itself embeds "\t" for its own tab-jump alignment;
        # what matters is the literal tab right before "status" survives
        assert "\tstatus=ok" in result


class TestEmbeddedTabAcrossPrefixOffsets:
    # captured once per offset: compression is legitimately sensitive to
    # where the tab stops fall, same as it is for any other content;
    # these pin down the exact result so a regression can't hide behind
    # "well it still compresses something"
    _EXPECTED = {
        0: "<〃\t〃\t〃\t><〃>=002\tstatus=ok",
        1: "<〃\t><〃\t〃\t><〃>=002\tstatus=ok",
        3: "<〃\t><〃\t〃\t><〃>=002<〃\t><〃>    =ok",
        5: "\t<〃\t〃\t〃\t><〃>=002\tstatus=ok",
        8: "<〃\t〃\t〃\t><〃>=002\tstatus=ok",
        13: "\t<〃\t〃\t〃\t><〃>=002\tstatus=ok",
        16: "<〃\t〃\t〃\t><〃>=002\tstatus=ok",
        20: "<〃\t><〃\t〃\t><〃>=002\tstatus=ok",
    }

    @pytest.mark.parametrize("prefix_len", sorted(_EXPECTED))
    def test_compression_matches_expected_at_every_prefix_offset(
        _, prefix_len
    ):
        a = "row\tsensor=cpu\tid=001\tstatus=ok"
        b = "row\tsensor=cpu\tid=002\tstatus=ok"
        result = _compress_second(a, b, prefix_len=prefix_len)
        assert result == TestEmbeddedTabAcrossPrefixOffsets._EXPECTED[
            prefix_len
        ]

    @pytest.mark.parametrize("prefix_len", sorted(_EXPECTED))
    def test_changed_digit_always_survives(_, prefix_len):
        a = "row\tsensor=cpu\tid=001\tstatus=ok"
        b = "row\tsensor=cpu\tid=002\tstatus=ok"
        result = _compress_second(a, b, prefix_len=prefix_len)
        assert "002" in result


class TestTabAtDivergencePoint:
    def test_tab_immediately_before_the_change_stays_literal(_):
        # the tab sits right where the two messages diverge, so it can
        # never be part of a common run and must always print raw
        a = "name\tX"
        b = "name\tY"
        assert _compress_second(a, b) == "name\tY"
