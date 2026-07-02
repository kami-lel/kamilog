"""
lp-validation_test.py

tests for ValueError guards in line-padding functions (shared across all
three callables)
"""

import pytest
from kamilog import (
    gen_line_padding_centered,
    gen_line_padding_left_just,
    gen_line_padding_right_just,
)


FUNCS = [
    gen_line_padding_centered,
    gen_line_padding_left_just,
    gen_line_padding_right_just,
]


class TestLinePaddingValidation:
    @pytest.mark.parametrize("func", FUNCS)
    def test_content_with_newline(_, func):
        with pytest.raises(ValueError, match="single line"):
            func("a\nb", "=", line_width=10)

    @pytest.mark.parametrize("func", FUNCS)
    def test_content_exceeds_line_width(_, func):
        with pytest.raises(ValueError, match="exceeds line_width"):
            func("abc", "=", line_width=2)

    @pytest.mark.parametrize("func", FUNCS)
    def test_padding_empty_string(_, func):
        with pytest.raises(ValueError, match="single character"):
            func("hi", "", line_width=10)

    @pytest.mark.parametrize("func", FUNCS)
    def test_padding_multi_char(_, func):
        with pytest.raises(ValueError, match="single character"):
            func("hi", "==", line_width=10)

    @pytest.mark.parametrize("func", FUNCS)
    def test_padding_space(_, func):
        with pytest.raises(ValueError, match="printable"):
            func("hi", " ", line_width=10)

    @pytest.mark.parametrize("func", FUNCS)
    @pytest.mark.parametrize("nonprintable", ["\n", "\t", "\x00", "\r"])
    def test_padding_nonprintable(_, func, nonprintable):
        with pytest.raises(ValueError, match="printable"):
            func("hi", nonprintable, line_width=10)
