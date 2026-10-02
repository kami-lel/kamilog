"""
badge-set_test.py

tests for `KamiLogger.set_persistent_badges` and `clear_persistent_badges` in `kamilog.py`
"""

import pytest

from kamilog.kamilog import KamiLogger


@pytest.fixture
def log():
    return KamiLogger("badge-set-test")


class TestSetBadges:
    def test_dft_is_empty(_, log):
        assert log._persistent_badges == ()

    def test_set_list_sorted_by_priority(_, log):
        log.set_persistent_badges(["auto", "dry"])
        assert log._persistent_badges == ("dry", "auto")

    def test_set_single_str(_, log):
        log.set_persistent_badges("deploy")
        assert log._persistent_badges == ("deploy",)

    def test_set_replaces_prev(_, log):
        log.set_persistent_badges(["dry"])
        log.set_persistent_badges(["force"])
        assert log._persistent_badges == ("force",)

    def test_set_drops_duplicates(_, log):
        log.set_persistent_badges(["dry", "dry"])
        assert log._persistent_badges == ("dry",)

    @pytest.mark.parametrize("unset", [(), (None,), ([],), ((),)])
    def test_unset_forms(_, log, unset):
        log.set_persistent_badges(["dry"])
        log.set_persistent_badges(*unset)
        assert log._persistent_badges == ()

    def test_clear_persistent_badges(_, log):
        log.set_persistent_badges(["dry", "yes"])
        log.clear_persistent_badges()
        assert log._persistent_badges == ()

    def test_state_is_per_logger(_, log):
        other = KamiLogger("badge-set-other")
        log.set_persistent_badges(["dry"])
        assert other._persistent_badges == ()
        assert KamiLogger._persistent_badges == ()
