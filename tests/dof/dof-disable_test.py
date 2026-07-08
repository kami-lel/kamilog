"""
dof-disable_test.py

tests for `_DiffOnlyMsgFilter` bypass via `disable_diff_only_compression`
in `kamilog.py`
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


class TestDisabledFilterHasNoEngine:
    def test_engine_is_none_when_disabled(_):
        f = _DiffOnlyMsgFilter(
            _StubFormatter(), threshold=1, disable_diff_only_compression=True
        )
        assert f._engine is None

    def test_engine_is_built_when_enabled(_):
        f = _DiffOnlyMsgFilter(
            _StubFormatter(), threshold=1, disable_diff_only_compression=False
        )
        assert f._engine is not None


class TestDisabledFilterPassesRecordsThrough:
    def test_repeated_compressible_messages_stay_uncompressed(_):
        f = _DiffOnlyMsgFilter(
            _StubFormatter(), threshold=1, disable_diff_only_compression=True
        )
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        r1 = _make_record(a)
        r2 = _make_record(b)
        f.filter(r1)
        f.filter(r2)
        assert r1.msg == a
        assert r2.msg == b

    def test_filter_still_returns_true(_):
        f = _DiffOnlyMsgFilter(
            _StubFormatter(), threshold=1, disable_diff_only_compression=True
        )
        assert f.filter(_make_record("anything")) is True
