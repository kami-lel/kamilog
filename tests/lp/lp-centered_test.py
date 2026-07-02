"""
lp-centered_test.py

tests for `gen_line_padding_centered` in `kamilog.py`
"""

from kamilog import AnsiRenderer, gen_line_padding_centered


class TestLinePaddingCentered:
    def test_even_remaining(_):
        result = gen_line_padding_centered("hi", "=", line_width=14)
        assert result == "====  hi  ===="

    def test_odd_remaining_extra_right(_):
        result = gen_line_padding_centered("hi", "=", line_width=11)
        assert result == "==  hi  ==="

    def test_empty_content(_):
        result = gen_line_padding_centered("", "=", line_width=6)
        assert result == "=    ="

    def test_content_fills_with_no_padding(_):
        result = gen_line_padding_centered("hi", "=", line_width=6)
        assert result == "  hi  "

    def test_output_length_equals_line_width(_):
        result = gen_line_padding_centered("hello", "-", line_width=20)
        assert len(result) == 20

    def test_default_line_width_is_80(_):
        result = gen_line_padding_centered("test", "*")
        assert len(result) == 80

    def test_reuses_passed_renderer(_):
        renderer = AnsiRenderer(None)
        result = gen_line_padding_centered(
            "test", "#", line_width=16, renderer=renderer
        )
        assert "#" in result
        assert "test" in result
