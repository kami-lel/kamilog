"""
logger-file-handler_test.py

tests for `getLogger` file-handler support in `kamilog.py`
"""

import logging
import uuid

from kamilog.kamilog import getLogger


def _flush(logger):
    for handler in logger.handlers:
        handler.flush()


class TestFileHandlerAttachment:
    def test_no_filename_keeps_two_handlers(_):
        logger = getLogger(uuid.uuid4().hex)
        assert len(logger.handlers) == 2

    def test_filename_adds_file_handler(_, tmp_path):
        path = tmp_path / "app.log"
        logger = getLogger(uuid.uuid4().hex, filename=str(path))
        assert len(logger.handlers) == 3
        assert isinstance(logger.handlers[-1], logging.FileHandler)

    def test_disable_console_gives_file_only(_, tmp_path):
        path = tmp_path / "app.log"
        logger = getLogger(
            uuid.uuid4().hex, filename=str(path), disable_console=True
        )
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)


class TestFileHandlerOutput:
    def test_file_receives_kamilog_format(_, tmp_path):
        path = tmp_path / "app.log"
        logger = getLogger(
            uuid.uuid4().hex, filename=str(path), disable_console=True
        )
        logger.setLevel(logging.DEBUG)  # let low Levels through
        logger.succ("hello")
        _flush(logger)
        content = path.read_text()
        assert "SUCC." in content  # padded Level name present
        assert "\033" not in content  # color always off in File

    def test_file_mode_write_truncates(_, tmp_path):
        path = tmp_path / "app.log"
        name = uuid.uuid4().hex
        logger = getLogger(name, filename=str(path), disable_console=True)
        logger.setLevel(logging.DEBUG)
        logger.info("only line")
        _flush(logger)
        path.write_text("stale content\n")  # simulate prior File data
        logger.handlers[0].close()
        logging.Logger.manager.loggerDict.pop(name, None)  # fresh logger
        logger = getLogger(
            name, filename=str(path), file_mode="w", disable_console=True
        )
        logger.setLevel(logging.DEBUG)
        logger.info("fresh line")
        _flush(logger)
        lines = path.read_text().splitlines()
        assert len(lines) == 1
        assert "fresh line" in lines[0]


class TestFileHandlerIdempotent:
    def test_repeated_call_does_not_duplicate_file_handler(_, tmp_path):
        path = tmp_path / "app.log"
        name = uuid.uuid4().hex
        getLogger(name, filename=str(path))
        logger = getLogger(name, filename=str(path))
        file_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
