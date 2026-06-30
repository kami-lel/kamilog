"""
lp-centered_test.py

tests for `print_line_padding_centered` in `kamilog.py`
"""

import io
from kamilog import print_line_padding_centered


class TestLinePaddingCentered:
    def test_even_remaining(_):
        out = io.StringIO()
        print_line_padding_centered("hi", "=", line_width=10, file=out)
        assert out.getvalue() == "====hi====\n"

    def test_odd_remaining_extra_right(_):
        out = io.StringIO()
        print_line_padding_centered("hi", "=", line_width=11, file=out)
        assert out.getvalue() == "====hi=====\n"

    def test_empty_content(_):
        out = io.StringIO()
        print_line_padding_centered("", "=", line_width=6, file=out)
        assert out.getvalue() == "======\n"

    def test_content_fills_exactly(_):
        out = io.StringIO()
        print_line_padding_centered("hi", "=", line_width=2, file=out)
        assert out.getvalue() == "hi\n"

    def test_output_length_equals_line_width(_):
        out = io.StringIO()
        print_line_padding_centered("hello", "-", line_width=20, file=out)
        line = out.getvalue().rstrip("\n")
        assert len(line) == 20

    def test_default_line_width_is_80(_):
        out = io.StringIO()
        print_line_padding_centered("test", "*", file=out)
        line = out.getvalue().rstrip("\n")
        assert len(line) == 80

    def test_custom_end(_):
        out = io.StringIO()
        print_line_padding_centered("hi", "=", line_width=10, end="", file=out)
        assert out.getvalue() == "====hi===="

    def test_custom_file(_):
        out = io.StringIO()
        print_line_padding_centered("test", "#", line_width=12, file=out)
        assert "#" in out.getvalue()
        assert "test" in out.getvalue()

    def test_flush_param(_):
        out = io.StringIO()
        print_line_padding_centered("x", ".", line_width=5, file=out,
                                    flush=True)
        assert out.getvalue() == "..x..\n"
