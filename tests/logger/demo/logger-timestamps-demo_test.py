"""
logger-timestamps-demo_test.py

tests for `KamiLogger`'s `datefmt` timestamp formats in `kamilog.py`;
excludes `relative_to` elapsed-time display, since it depends on real
sleep durations and can't be pinned to an exact string
"""

import contextlib
import io
import re

import pytest

import kamilog

_TIME_RE = re.compile(
    r"(?:\d{4}-\d{2}-\d{2} )?\d{2}:\d{2}:\d{2}(?:\.\d{3})?"
)

_DATEFMT_CASES = [
    (
        "logger-timestamps-demo-time",
        {},
        "HH:MM:SS (default)",
        "<TIME> INFO  logger-timestamps-demo-time: HH:MM:SS (default)",
    ),
    (
        "logger-timestamps-demo-none",
        {"datefmt": None},
        "no timestamp",
        "INFO  logger-timestamps-demo-none: no timestamp",
    ),
    (
        "logger-timestamps-demo-time-ms",
        {"datefmt": kamilog.DATEFMT_TIME_MS},
        "HH:MM:SS.mmm",
        "<TIME> INFO  logger-timestamps-demo-time-ms: HH:MM:SS.mmm",
    ),
    (
        "logger-timestamps-demo-datetime",
        {"datefmt": kamilog.DATEFMT_DATETIME},
        "YYYY-MM-DD HH:MM:SS",
        "<TIME> INFO  logger-timestamps-demo-datetime: YYYY-MM-DD HH:MM:SS",
    ),
    (
        "logger-timestamps-demo-datetime-ms",
        {"datefmt": kamilog.DATEFMT_DATETIME_MS},
        "YYYY-MM-DD HH:MM:SS.mmm",
        "<TIME> INFO  logger-timestamps-demo-datetime-ms: YYYY-MM-DD HH:MM:SS.mmm",
    ),
]


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


def _run_and_capture(name, kwargs, message):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        log = kamilog.getLogger(name, **kwargs)
        log.setLevel(kamilog.DEBUG)
        log.propagate = False
        log.info(message)
    return out.getvalue(), err.getvalue()


class TestDatefmtFormats:
    @pytest.mark.parametrize("name, kwargs, message, expected", _DATEFMT_CASES)
    def test_line(_, name, kwargs, message, expected):
        out, err = _run_and_capture(name, kwargs, message)
        assert _mask_time(out) == expected + "\n"
        assert err == ""
