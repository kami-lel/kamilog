"""
badge-normalize_test.py

tests for `_normalize_badges` in `kamilog`
"""

from kamilog.badges import _normalize_badges


class TestNormalizeBadges:
    def test_single_str(_):
        assert _normalize_badges("dry") == ("dry",)

    def test_none_and_empty(_):
        assert _normalize_badges(None) == ()
        assert _normalize_badges([]) == ()
        assert _normalize_badges(()) == ()

    def test_natives_sorted_by_descending_priority(_):
        assert _normalize_badges(["auto", "dry", "force"]) == (
            "force",
            "dry",
            "auto",
        )

    def test_customs_after_natives_in_given_order(_):
        assert _normalize_badges(["zeta", "auto", "alpha"]) == (
            "auto",
            "zeta",
            "alpha",
        )

    def test_duplicates_dropped(_):
        assert _normalize_badges(["dry", "dry", "x", "x"]) == ("dry", "x")

    def test_mixed_native_and_custom(_):
        got = _normalize_badges(("deploy", "yes", "dry", "deploy", "bg"))
        assert got == ("dry", "bg", "deploy", "yes")

    def test_accepts_generator(_):
        assert _normalize_badges(b for b in ("bg", "dry")) == ("dry", "bg")

    def test_returns_tuple(_):
        assert isinstance(_normalize_badges(["dry"]), tuple)
