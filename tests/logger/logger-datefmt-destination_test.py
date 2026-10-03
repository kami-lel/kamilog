"""
logger-datefmt-destination_test.py

tests for `getLogger` per-destination `datefmt` default in `kamilog`
"""

import logging
import re
import time
import uuid

from kamilog import DATEFMT_TIME, getLogger

FILE_STAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} INFO"
CONSOLE_STAMP = r"\d{2}:\d{2}:\d{2}"


def _flush(logger):
    for handler in logger.handlers:
        handler.flush()


def _log_once(tmp_path, **kwargs):
    """log one INFO record, return the console text & file text"""
    path = tmp_path / "app.log"
    logger = getLogger(uuid.uuid4().hex, filename=str(path), **kwargs)
    logger.setLevel(logging.INFO)
    logger.info("hello")
    _flush(logger)
    return path.read_text()


class TestAutoDefault:
    def test_console_has_no_timestamp(_, tmp_path, capsys):
        _log_once(tmp_path)
        out = capsys.readouterr().out
        assert re.fullmatch(r"INFO  \S+: hello\n", out)

    def test_file_has_datetime_ms(_, tmp_path):
        content = _log_once(tmp_path)
        assert re.match(FILE_STAMP, content)


class TestExplicitDatefmt:
    def test_applies_to_console_and_file(_, tmp_path, capsys):
        content = _log_once(tmp_path, datefmt=DATEFMT_TIME)
        out = capsys.readouterr().out
        assert re.match(CONSOLE_STAMP + r" INFO", out)
        assert re.match(CONSOLE_STAMP + r" INFO", content)

    def test_none_disables_both(_, tmp_path, capsys):
        content = _log_once(tmp_path, datefmt=None)
        out = capsys.readouterr().out
        assert out.startswith("INFO")
        assert content.startswith("INFO")


class TestRelativeTo:
    def test_applies_to_console_and_file(_, tmp_path, capsys):
        content = _log_once(tmp_path, relative_to=time.time())
        out = capsys.readouterr().out
        assert re.match(r"\+", out.lstrip())
        assert re.match(r"\+", content.lstrip())
