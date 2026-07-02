"""
lp-right_just_test.py

tests for `gen_line_padding_right_just` in `kamilog.py`
"""

from kamilog import AnsiRenderer, gen_line_padding_right_just


class TestLinePaddingRightJust:
    def test_normal(_):
        result = gen_line_padding_right_just("hi", "=", line_width=10)
        assert result == "======  hi"

    def test_empty_content(_):
        result = gen_line_padding_right_just("", "=", line_width=6)
        assert result == "====  "

    def test_content_fills_with_no_padding(_):
        result = gen_line_padding_right_just("hi", "=", line_width=4)
        assert result == "  hi"

    def test_output_length(_):
        result = gen_line_padding_right_just("hello", "-", line_width=20)
        assert len(result) == 20

    def test_default_line_width_is_80(_):
        result = gen_line_padding_right_just("test", "*")
        assert len(result) == 80

    def test_reuses_passed_renderer(_):
        renderer = AnsiRenderer(None)
        result = gen_line_padding_right_just(
            "test", "#", line_width=12, renderer=renderer
        )
        assert result.endswith("test")
