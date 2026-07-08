"""
cb-zero-demo_test.py

tests for `gen_comment_banner_zero` (CB0 multi-line boxed banner) in
`kamilog.py`
"""

import pytest

from kamilog.kamilog import gen_comment_banner_zero


class TestSimpleBanner:
    _lines = gen_comment_banner_zero(["Title"], line_width=20).split("\n")
    _expected = [
        "####################",
        "# Title",
        "####################",
    ]

    @pytest.mark.parametrize("i", range(len(_expected)))
    def test_line(_, i):
        assert TestSimpleBanner._lines[i] == TestSimpleBanner._expected[i]


class TestMultiLineBanner:
    _lines = gen_comment_banner_zero(
        [
            "Section Title",
            "description line 1",
            "description line 2",
        ],
        line_width=30,
    ).split("\n")
    _expected = [
        "##############################",
        "# Section Title",
        "# description line 1",
        "# description line 2",
        "##############################",
    ]

    @pytest.mark.parametrize("i", range(len(_expected)))
    def test_line(_, i):
        assert TestMultiLineBanner._lines[i] == TestMultiLineBanner._expected[i]


class TestWideBanner:
    _lines = gen_comment_banner_zero(
        [
            "Feature Implementation",
            "Author: Development Team",
            "Status: In Progress",
        ],
        line_width=50,
    ).split("\n")
    _expected = [
        "##################################################",
        "# Feature Implementation",
        "# Author: Development Team",
        "# Status: In Progress",
        "##################################################",
    ]

    @pytest.mark.parametrize("i", range(len(_expected)))
    def test_line(_, i):
        assert TestWideBanner._lines[i] == TestWideBanner._expected[i]
