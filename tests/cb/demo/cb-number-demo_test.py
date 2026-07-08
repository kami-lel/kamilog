"""
cb-number-demo_test.py

tests for `gen_comment_banner_centered`'s numeric padding shortcuts
(1-5) in `kamilog.py`
"""

import pytest

from kamilog.kamilog import gen_comment_banner_centered

_PADDING_CASES = [
    (
        1,
        "###################################  title  ####################################",
    ),
    (
        2,
        "===================================  title  ====================================",
    ),
    (
        3,
        "***********************************  title  ************************************",
    ),
    (
        4,
        "+++++++++++++++++++++++++++++++++++  title  ++++++++++++++++++++++++++++++++++++",
    ),
    (
        5,
        "-----------------------------------  title  ------------------------------------",
    ),
]


class TestNumericPaddingShortcuts:
    @pytest.mark.parametrize("padding, expected", _PADDING_CASES)
    def test_line(_, padding, expected):
        assert gen_comment_banner_centered("title", padding) == expected
