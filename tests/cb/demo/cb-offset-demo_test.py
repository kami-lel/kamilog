"""
cb-offset-demo_test.py

tests for `gen_comment_banner_centered`'s `horizontal_offset` parameter
in `kamilog.py`
"""

import pytest

from kamilog.kamilog import gen_comment_banner_centered

_OFFSET_CASES = [
    (
        "results",
        72,
        -4,
        "==========================  results  ===================================",
    ),
    (
        "results",
        72,
        4,
        "==================================  results  ===========================",
    ),
    ("hi", 20, 2, "=========  hi  ====="),
    ("hi", 20, -2, "=====  hi  ========="),
    ("hi", 20, 0, "=======  hi  ======="),
]


class TestHorizontalOffset:
    @pytest.mark.parametrize("content, line_width, offset, expected", _OFFSET_CASES)
    def test_line(_, content, line_width, offset, expected):
        assert (
            gen_comment_banner_centered(
                content, "=", line_width=line_width, horizontal_offset=offset
            )
            == expected
        )

    def test_out_of_range_raises(_):
        # offset larger than half the fill pushes right side below zero
        with pytest.raises(ValueError):
            gen_comment_banner_centered("hi", "=", line_width=20, horizontal_offset=99)
