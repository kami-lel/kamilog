"""
dof-warmup_test.py

tests for `_DiffOnlyEngine.process` warmup behavior in `kamilog.py`
"""

from kamilog.kamilog import _DiffOnlyEngine


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


class _StubRecord:
    def __init__(self, message):
        self._message = message

    def getMessage(self):
        return self._message


class TestWarmupPassthrough:
    def test_first_call_returns_original_message(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=3)
        masked = engine.process(_StubRecord("hello world"))
        assert masked == "hello world"

    def test_all_calls_within_threshold_pass_through(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=3)
        messages = ["a" * 20 + "/one", "a" * 20 + "/two", "a" * 20 + "/three"]
        masked = [engine.process(_StubRecord(m)) for m in messages]
        assert masked == messages

    def test_history_grows_during_warmup(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=3)
        engine.process(_StubRecord("first"))
        engine.process(_StubRecord("second"))
        assert list(engine._history) == ["first", "second"]


class TestActivationAfterThreshold:
    def test_threshold_one_compresses_from_second_call(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=1)
        a = "a" * 16 + "/bbb" + "X"
        b = "a" * 16 + "/bbb" + "Y"
        first = engine.process(_StubRecord(a))
        second = engine.process(_StubRecord(b))
        assert first == a
        assert second != b

    def test_history_maxlen_matches_threshold(_):
        engine = _DiffOnlyEngine(_StubFormatter(), threshold=5)
        assert engine._history.maxlen == 5
