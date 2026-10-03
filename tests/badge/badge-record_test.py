"""
badge-record_test.py

tests for the `KamiLogger._log` badge kwargs in `kamilog`
"""

import logging

import pytest

from kamilog import KamiLogger

_LEVEL_METHODS = (
    "debug",
    "enter",
    "skip",
    "succ",
    "pass_",
    "info",
    "note",
    "tip",
    "done",
    "hint",
    "important",
    "warning",
    "caution",
    "error",
    "fail",
    "critical",
)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=1)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def cap():
    return _Capture()


@pytest.fixture
def log(cap):
    logger = KamiLogger("badge-record-test")
    logger.setLevel(1)
    logger.propagate = False
    logger.addHandler(cap)
    return logger


class TestRecordBadges:
    def test_no_badges_gives_empty_tuple(_, log, cap):
        log.info("m")
        assert cap.records[0].badges == ()

    def test_run_wide_lands_on_record(_, log, cap):
        log.set_persistent_badges(["dry"])
        log.info("m")
        assert cap.records[0].badges == ("dry",)

    def test_per_call_str(_, log, cap):
        log.done("m", badges="deploy")
        assert cap.records[0].badges == ("deploy",)

    def test_per_call_appends_after_run_wide_in_given_order(_, log, cap):
        log.set_persistent_badges(["auto"])
        log.done("m", badges=["force", "x"])
        assert cap.records[0].badges == ("auto", "force", "x")

    def test_per_call_duplicate_of_run_wide_kept_once(_, log, cap):
        log.set_persistent_badges(["dry"])
        log.info("m", badges=["dry"])
        assert cap.records[0].badges == ("dry",)

    def test_inherit_false_hides_run_wide_for_one_record(_, log, cap):
        log.set_persistent_badges(["dry"])
        log.info("m", is_inheriting_badges=False)
        log.info("m")
        assert cap.records[0].badges == ()
        assert cap.records[1].badges == ("dry",)

    def test_inherit_false_keeps_per_call(_, log, cap):
        log.set_persistent_badges(["dry"])
        log.info("m", badges="yes", is_inheriting_badges=False)
        assert cap.records[0].badges == ("yes",)

    def test_log_method_accepts_kwargs(_, log, cap):
        log.log(logging.INFO, "m", badges=["dry"])
        assert cap.records[0].badges == ("dry",)

    def test_extra_is_preserved_and_not_mutated(_, log, cap):
        extra = {"k": 1}
        log.info("m", extra=extra, badges="dry")
        assert cap.records[0].k == 1
        assert extra == {"k": 1}

    def test_msg_args_still_formatted(_, log, cap):
        log.info("a %s", "b", badges="dry")
        assert cap.records[0].getMessage() == "a b"

    @pytest.mark.parametrize("name", _LEVEL_METHODS)
    def test_every_level_method_accepts_badges(_, log, cap, name):
        getattr(log, name)("m", badges=["dry"])
        assert cap.records[0].badges == ("dry",)


class TestCallerInfo:
    def test_lineno_and_func_name_point_at_caller(_, log, cap):
        def call_site():
            log.done("m", badges="dry")  # marker line
            return None

        call_site()
        record = cap.records[0]
        assert record.funcName == "call_site"
        assert record.filename == "badge-record_test.py"
        with open(__file__) as fh:
            line = fh.read().splitlines()[record.lineno - 1]
        assert "marker line" in line

    def test_generic_log_points_at_caller(_, log, cap):
        def call_site():
            log.log(logging.INFO, "m")

        call_site()
        assert cap.records[0].funcName == "call_site"

    def test_explicit_stacklevel_still_honored(_, log, cap):
        def inner():
            log.info("m", stacklevel=2)

        def outer():
            inner()

        outer()
        assert cap.records[0].funcName == "outer"
