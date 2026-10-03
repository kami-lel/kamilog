"""
badge-normalize_test.py

tests for `normalize_badges` in `kamilog`
"""

from kamilog.badges import normalize_badges


class TestNormalizeBadges:
    def test_single_str(_):
        assert normalize_badges("dry") == ("dry",)

    def test_none_and_empty(_):
        assert normalize_badges(None) == ()
        assert normalize_badges([]) == ()
        assert normalize_badges(()) == ()

    def test_order_preserved(_):
        assert normalize_badges(["auto", "dry", "force"]) == (
            "auto",
            "dry",
            "force",
        )

    def test_natives_and_customs_keep_given_order(_):
        assert normalize_badges(["zeta", "auto", "alpha"]) == (
            "zeta",
            "auto",
            "alpha",
        )

    def test_duplicates_dropped(_):
        assert normalize_badges(["dry", "dry", "x", "x"]) == ("dry", "x")

    def test_mixed_native_and_custom(_):
        got = normalize_badges(("deploy", "yes", "dry", "deploy", "bg"))
        assert got == ("deploy", "yes", "dry", "bg")

    def test_accepts_generator(_):
        assert normalize_badges(b for b in ("bg", "dry")) == ("bg", "dry")

    def test_returns_tuple(_):
        assert isinstance(normalize_badges(["dry"]), tuple)
