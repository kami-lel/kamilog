"""
deed-track-handle_test.py

tests for the `act` handle and `suppress` of tracked deeds in `kamilog.py`
"""

import logging
import uuid

import pytest


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _make_logger():
    logger = logging.getLogger(uuid.uuid4().hex)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    cap = _Capture()
    logger.addHandler(cap)
    return logger, cap


class TestLateArguments:
    def test_download_example(_):
        logger, cap = _make_logger()
        with logger.track.download("http://x/a.zip") as act:
            act.set(destination="a.zip")
        assert cap.records[0].getMessage() == "download http://x/a.zip -> a.zip"

    def test_missing_late_arg_drops_segment_on_success(_):
        logger, cap = _make_logger()
        with logger.track.download("http://x/a.zip"):
            pass
        assert cap.records[0].getMessage() == "download http://x/a.zip"

    def test_failure_before_name_chosen(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.download("http://x/a.zip"):
                raise OSError("down")
        assert cap.records[0].getMessage() == (
            "fail to download http://x/a.zip: OSError: down"
        )

    def test_late_arg_used_on_failure(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.download("http://x/a.zip") as act:
                act.set(destination="a.zip")
                raise OSError("cut")
        assert cap.records[0].getMessage() == (
            "fail to download http://x/a.zip -> a.zip: OSError: cut"
        )

    def test_set_twice_last_wins(_):
        logger, cap = _make_logger()
        with logger.track.download("u") as act:
            act.set(destination="one")
            act.set(destination="two")
        assert cap.records[0].getMessage() == "download u -> two"

    def test_set_unknown_name_rejected(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            with logger.track.download("u") as act:
                act.set(dst="a")

    def test_set_already_positional_rejected(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            with logger.track.download("u", "a") as act:
                act.set(destination="b")

    def test_set_may_fill_leading_arg_omitted_at_entry(_):
        logger, cap = _make_logger()
        with logger.track.create_file() as act:
            act.set(path="x")
        assert cap.records[0].getMessage() == "create x"

    def test_handle_exposes_set_and_fail_only(_):
        logger, _cap = _make_logger()
        with logger.track.rm_file("a") as act:
            public = {n for n in dir(act) if not n.startswith("_")}
        assert public == {"set", "fail"}


class TestFailAsValue:
    def test_run_command_example(_):
        logger, cap = _make_logger()
        with logger.track.run_command("make") as act:
            act.fail("exit 2")
        rec = cap.records[0]
        assert rec.getMessage() == "fail to run make: exit 2"
        assert rec.levelno == logging.ERROR
        assert rec.exc_info is None

    def test_no_exception_raised(_):
        logger, _cap = _make_logger()
        with logger.track.run_command("make") as act:
            act.fail("exit 1")

    def test_fail_uses_err_level_override(_):
        logger, cap = _make_logger()
        with logger.track.run_command("make", err_level=logging.WARNING) as a:
            a.fail("exit 1")
        assert cap.records[0].levelno == logging.WARNING

    def test_fail_default_err_level_follows_deed(_):
        logger, cap = _make_logger()
        with logger.track.rm_file("a") as act:
            act.fail("busy")
        assert cap.records[0].levelno == logging.WARNING

    def test_fail_with_late_arg(_):
        logger, cap = _make_logger()
        with logger.track.download("u") as act:
            act.set(destination="a")
            act.fail("status 404")
        assert cap.records[0].getMessage() == (
            "fail to download u -> a: status 404"
        )

    def test_exception_wins_over_fail(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.rm_file("a") as act:
                act.fail("busy")
                raise OSError("x")
        assert len(cap.records) == 1
        assert cap.records[0].getMessage() == "fail to delete a: OSError: x"

    def test_call_site_is_with_line(_):
        logger, cap = _make_logger()
        with logger.track.rm_file("a") as act:  # site-fail
            act.fail("busy")
        rec = cap.records[0]
        assert rec.funcName == "test_call_site_is_with_line"
        assert rec.lineno == _find_line("# site-fail")


class TestSuppress:
    def test_swallows_exception_after_logging(_):
        logger, cap = _make_logger()
        with logger.track.rm_file("a", suppress=True):
            raise OSError("x")
        rec = cap.records[0]
        assert rec.getMessage() == "fail to delete a: OSError: x"
        assert rec.exc_info[0] is OSError

    def test_code_after_block_runs(_):
        logger, _cap = _make_logger()
        ran = []
        with logger.track.rm_file("a", suppress=True):
            raise OSError("x")
        ran.append(1)
        assert ran == [1]

    def test_default_propagates(_):
        logger, _cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.rm_file("a"):
                raise OSError("x")

    @pytest.mark.parametrize("exc", [KeyboardInterrupt, SystemExit])
    def test_base_exceptions_not_suppressed(_, exc):
        logger, cap = _make_logger()
        with pytest.raises(exc):
            with logger.track.rm_file("a", suppress=True):
                raise exc()
        assert cap.records == []

    def test_success_unaffected(_):
        logger, cap = _make_logger()
        with logger.track.rm_file("a", suppress=True):
            pass
        assert cap.records[0].getMessage() == "delete a"

    def test_err_level_with_suppress(_):
        logger, cap = _make_logger()
        with logger.track.cp_file(
            "a", "b", suppress=True, err_level=logging.WARNING
        ):
            raise OSError("x")
        assert cap.records[0].levelno == logging.WARNING

    def test_plain_form_rejects_suppress(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.rm_file("a", suppress=True)


def _find_line(marker):
    """1-based number of the line ending with comment `marker`"""
    with open(__file__, encoding="utf-8") as f:
        hits = [i for i, ln in enumerate(f, 1) if ln.rstrip().endswith(marker)]
    return hits[0]
