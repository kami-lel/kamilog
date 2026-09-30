"""
deed-track-core_test.py

tests for the track form of the deed methods of `KamiLogger` in `kamilog.py`
"""

import logging
import uuid

import pytest

from kamilog.kamilog import _DEEDS, KamiLogger


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


class TestTrackNamespace:
    @pytest.mark.parametrize("name", list(_DEEDS))
    def test_every_deed_has_track_form(_, name):
        logger, _cap = _make_logger()
        assert callable(getattr(logger.track, name))

    def test_root_logger_has_track(_):
        assert callable(logging.root.track.cp_file)

    def test_property_on_class(_):
        assert isinstance(KamiLogger.track, property)


class TestTrackSuccess:
    def test_line_written_at_exit_not_entry(_):
        logger, cap = _make_logger()
        with logger.track.cp_file("a", "b"):
            assert cap.records == []
        assert [r.getMessage() for r in cap.records] == ["copy a -> b"]

    def test_default_level(_):
        logger, cap = _make_logger()
        with logger.track.rm_file("a"):
            pass
        assert cap.records[0].levelno == logging.WARNING

    def test_level_override(_):
        logger, cap = _make_logger()
        with logger.track.cp_file("a", "b", level=logging.DEBUG):
            pass
        assert cap.records[0].levelno == logging.DEBUG

    def test_omitted_destination(_):
        logger, cap = _make_logger()
        with logger.track.download("http://x/a"):
            pass
        assert cap.records[0].getMessage() == "download http://x/a"

    def test_badges(_):
        logger, cap = _make_logger()
        logger.set_badges("force")
        with logger.track.cp_file("a", "b", badges="dry"):
            pass
        assert cap.records[0].badges == ("force", "dry")

    def test_not_inheriting_badges(_):
        logger, cap = _make_logger()
        logger.set_badges("force")
        with logger.track.cp_file("a", "b", is_inheriting_badges=False):
            pass
        assert cap.records[0].badges == ()

    def test_disabled_level_logs_nothing(_):
        logger, cap = _make_logger()
        logger.setLevel(logging.ERROR)
        with logger.track.cp_file("a", "b"):
            pass
        assert cap.records == []


class TestTrackFailure:
    def test_permission_error_example(_):
        logger, cap = _make_logger()
        err = PermissionError(13, "Permission denied", "/root/a.txt")
        with pytest.raises(PermissionError):
            with logger.track.cp_file("a.txt", "/root/a.txt"):
                raise err
        assert len(cap.records) == 1
        rec = cap.records[0]
        assert rec.levelno == logging.ERROR
        assert rec.getMessage() == (
            "fail to copy a.txt -> /root/a.txt: PermissionError: "
            "[Errno 13] Permission denied: '/root/a.txt'"
        )

    def test_traceback_attached(_):
        logger, cap = _make_logger()
        with pytest.raises(ValueError):
            with logger.track.rm_file("a"):
                raise ValueError("boom")
        exc_type, exc_value, tb = cap.records[0].exc_info
        assert exc_type is ValueError
        assert str(exc_value) == "boom"
        assert tb is not None

    def test_exception_propagates_same_object(_):
        logger, _cap = _make_logger()
        err = RuntimeError("x")
        with pytest.raises(RuntimeError) as info:
            with logger.track.create_file("a"):
                raise err
        assert info.value is err

    def test_empty_detail_shows_type_only(_):
        logger, cap = _make_logger()
        with pytest.raises(ValueError):
            with logger.track.rm_file("a"):
                raise ValueError()
        assert cap.records[0].getMessage() == "fail to delete a: ValueError"

    def test_default_err_level_follows_deed(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.rm_file("a"):
                raise OSError("x")
        with pytest.raises(OSError):
            with logger.track.create_file("a"):
                raise OSError("x")
        assert [r.levelno for r in cap.records] == [
            logging.WARNING,
            logging.ERROR,
        ]

    def test_err_level_override_leaves_level_alone(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.cp_file(
                "a", "b", level=logging.DEBUG, err_level=logging.WARNING
            ):
                raise OSError("x")
        assert cap.records[0].levelno == logging.WARNING

    def test_level_override_never_touches_failure(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.cp_file("a", "b", level=logging.DEBUG):
                raise OSError("x")
        assert cap.records[0].levelno == logging.ERROR

    @pytest.mark.parametrize("exc", [KeyboardInterrupt, SystemExit])
    def test_base_exceptions_log_nothing(_, exc):
        logger, cap = _make_logger()
        with pytest.raises(exc):
            with logger.track.cp_file("a", "b"):
                raise exc()
        assert cap.records == []

    def test_failure_badges(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.cp_file("a", "b", badges="dry"):
                raise OSError("x")
        assert cap.records[0].badges == ("dry",)


class TestTrackArguments:
    def test_too_many_args_raise_at_call(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.track.rm_file("a", "b")

    def test_suppress_not_yet_a_keyword_of_plain(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.rm_file("a", err_level=logging.ERROR)


class TestTrackCallSite:
    def test_success_points_at_with_line(_):
        logger, cap = _make_logger()
        with logger.track.cp_file("a", "b"):  # site-success
            pass
        rec = cap.records[0]
        assert rec.filename == "deed-track-core_test.py"
        assert rec.funcName == "test_success_points_at_with_line"
        assert rec.lineno == _find_line("# site-success")

    def test_failure_points_at_with_line(_):
        logger, cap = _make_logger()
        with pytest.raises(OSError):
            with logger.track.cp_file("a", "b"):  # site-failure
                raise OSError("x")
        rec = cap.records[0]
        assert rec.funcName == "test_failure_points_at_with_line"
        assert rec.lineno == _find_line("# site-failure")


def _find_line(marker):
    """1-based number of the line ending with comment `marker`"""
    with open(__file__, encoding="utf-8") as f:
        hits = [i for i, ln in enumerate(f, 1) if ln.rstrip().endswith(marker)]
    return hits[0]
