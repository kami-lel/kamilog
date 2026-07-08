"""
dof-process_test.py

end-to-end tests for `_DiffOnlyMsgFilter.filter` in `kamilog.py`
"""

import logging

from kamilog.kamilog import _DiffOnlyMsgFilter


class _StubEngine:
    def count_prefix_chars(self, record):
        return 0


class _StubPalette:
    def color_grey(self, text):
        return text


class _StubFormatter:
    def __init__(self):
        self.engine = _StubEngine()
        self.palette = _StubPalette()


def _make_record(message, args=()):
    return logging.LogRecord("x", logging.INFO, "path", 1, message, args, None)


class TestFilterMutatesRecordInPlace:
    def test_msg_is_replaced_with_masked_message(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=1)
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        f.filter(_make_record(a))
        r2 = _make_record(b)
        f.filter(r2)
        assert r2.msg == "〃\t〃\t/bbbY"

    def test_args_are_always_cleared(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=3)
        record = _make_record("hello %s", ("world",))
        f.filter(record)
        assert record.args == ()

    def test_args_are_interpolated_into_msg_before_clearing(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=3)
        record = _make_record("hello %s", ("world",))
        f.filter(record)
        assert record.msg == "hello world"

    def test_filter_always_returns_true(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=3)
        assert f.filter(_make_record("anything")) is True


class TestFilterWarmupThenCompress:
    def test_messages_within_threshold_are_untouched(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=3)
        messages = ["first/one", "second/two", "third/three"]
        records = [_make_record(m) for m in messages]
        for record in records:
            f.filter(record)
        assert [r.msg for r in records] == messages

    def test_message_after_threshold_is_compressed(_):
        f = _DiffOnlyMsgFilter(_StubFormatter(), threshold=1)
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        r1 = _make_record(a)
        r2 = _make_record(b)
        f.filter(r1)
        f.filter(r2)
        assert r1.msg == a
        assert r2.msg != b
