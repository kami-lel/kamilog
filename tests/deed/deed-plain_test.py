"""
deed-plain_test.py

tests for the plain-form deed methods of `KamiLogger` in `kamilog.py`
"""

import logging
import uuid

import pytest

from kamilog.kamilog import _DEEDS, SKIP, KamiLogger


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


class TestPlainMethodsExist:
    @pytest.mark.parametrize("name", list(_DEEDS))
    def test_method_on_logger(_, name):
        assert callable(getattr(KamiLogger, name))
        assert getattr(KamiLogger, name).__name__ == name

    def test_root_logger_has_methods(_):
        assert callable(logging.root.cp_file)


class TestPlainMessageAndLevel:
    def test_cp_file_info(_):
        logger, cap = _make_logger()
        logger.cp_file("a", "b")
        rec = cap.records[0]
        assert rec.getMessage() == "copy a -> b"
        assert rec.levelno == logging.INFO

    def test_rm_file_warning(_):
        logger, cap = _make_logger()
        logger.rm_file("a")
        assert cap.records[0].getMessage() == "delete a"
        assert cap.records[0].levelno == logging.WARNING

    def test_skip_file_skip_level(_):
        logger, cap = _make_logger()
        logger.skip_file("a")
        assert cap.records[0].levelno == int(SKIP)

    def test_omitted_destination(_):
        logger, cap = _make_logger()
        logger.download("http://x/a")
        assert cap.records[0].getMessage() == "download http://x/a"

    @pytest.mark.parametrize("name", list(_DEEDS))
    def test_default_level_matches_table(_, name):
        logger, cap = _make_logger()
        getattr(logger, name)("x")
        assert cap.records[0].levelno == int(_DEEDS[name].level)

    def test_percent_in_arg_is_literal(_):
        logger, cap = _make_logger()
        logger.create_file("100%s.txt")
        assert cap.records[0].getMessage() == "create 100%s.txt"

    def test_level_override(_):
        logger, cap = _make_logger()
        logger.rm_file("a", level=logging.DEBUG)
        assert cap.records[0].levelno == logging.DEBUG

    def test_disabled_level_logs_nothing(_):
        logger, cap = _make_logger()
        logger.setLevel(logging.ERROR)
        logger.cp_file("a", "b")
        assert cap.records == []


class TestPlainKeywords:
    def test_badges(_):
        logger, cap = _make_logger()
        logger.cp_file("a", "b", badges="dry")
        assert cap.records[0].badges == ("dry",)

    def test_persistent_badges_inherited(_):
        logger, cap = _make_logger()
        logger.set_persistent_badges("force")
        logger.cp_file("a", "b", badges="dry")
        assert cap.records[0].badges == ("force", "dry")

    def test_not_inheriting_badges(_):
        logger, cap = _make_logger()
        logger.set_persistent_badges("force")
        logger.cp_file("a", "b", is_inheriting_badges=False)
        assert cap.records[0].badges == ()

    def test_err_level_rejected(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.cp_file("a", "b", err_level=logging.ERROR)

    def test_suppress_rejected(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.cp_file("a", "b", suppress=True)

    def test_too_many_args_rejected(_):
        logger, _cap = _make_logger()
        with pytest.raises(TypeError):
            logger.rm_file("a", "b")


class TestPlainCallSite:
    def test_record_points_at_caller(_):
        logger, cap = _make_logger()
        logger.cp_file("a", "b")
        rec = cap.records[0]
        assert rec.filename == "deed-plain_test.py"
        assert rec.funcName == "test_record_points_at_caller"
