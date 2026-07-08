"""
cb-demo_test.py

tests for `gen_comment_banner_centered`, `gen_comment_banner_left_just`,
and `gen_comment_banner_right_just` in `kamilog.py`
"""

import pytest

from kamilog.kamilog import (
    gen_comment_banner_centered,
    gen_comment_banner_left_just,
    gen_comment_banner_right_just,
)

_CENTERED_CASES = [
    (
        "hello",
        "=",
        80,
        "===================================  hello  ====================================",
    ),
    (
        "release v2.0",
        "*",
        40,
        "************  release v2.0  ************",
    ),
    ("done", "-", 24, "--------  done  --------"),
]

_LEFT_JUST_CASES = [
    (
        "hello",
        "=",
        80,
        "hello  =========================================================================",
    ),
    (
        "release v2.0",
        ".",
        40,
        "release v2.0  ..........................",
    ),
    ("done", "-", 24, "done  ------------------"),
]

_RIGHT_JUST_CASES = [
    (
        "hello",
        "=",
        80,
        "=========================================================================  hello",
    ),
    (
        "release v2.0",
        ".",
        40,
        "..........................  release v2.0",
    ),
    ("done", "-", 24, "------------------  done"),
]


class TestCommentBannerCentered:
    @pytest.mark.parametrize("content, padding, line_width, expected", _CENTERED_CASES)
    def test_line(_, content, padding, line_width, expected):
        assert (
            gen_comment_banner_centered(content, padding, line_width=line_width)
            == expected
        )


class TestCommentBannerLeftJustified:
    @pytest.mark.parametrize("content, padding, line_width, expected", _LEFT_JUST_CASES)
    def test_line(_, content, padding, line_width, expected):
        assert (
            gen_comment_banner_left_just(content, padding, line_width=line_width)
            == expected
        )


class TestCommentBannerRightJustified:
    @pytest.mark.parametrize("content, padding, line_width, expected", _RIGHT_JUST_CASES)
    def test_line(_, content, padding, line_width, expected):
        assert (
            gen_comment_banner_right_just(content, padding, line_width=line_width)
            == expected
        )
