"""
logger-timestamps-demo_test.py

golden test for `examples/logger/logger-timestamps_demo.py`; locks in
the exact stdout of the ``datefmt formats`` section (timestamps masked,
since they vary by run) so future changes to timestamp formatting
can't silently drift.

the ``relative_to elapsed time`` section is excluded, since its
elapsed-time values depend on real sleep durations and can't be
pinned to an exact string
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "logger"
    / "logger-timestamps_demo.py"
)

_TIME_RE = re.compile(r"(?:\d{4}-\d{2}-\d{2} )?\d{2}:\d{2}:\d{2}(?:\.\d{3})?")


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


_EXPECTED_DATEFMT_SECTION = """\
##############################  datefmt formats  ###############################
<TIME> INFO  app.time: HH:MM:SS (default)
INFO  app.none: no timestamp
<TIME> INFO  app.time_ms: HH:MM:SS.mmm
<TIME> INFO  app.datetime: YYYY-MM-DD HH:MM:SS
<TIME> INFO  app.datetime_ms: YYYY-MM-DD HH:MM:SS.mmm
"""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestLoggerTimestampsDemoOutput:
    def test_datefmt_section_matches_exactly(_):
        result = _run_script()
        masked = _mask_time(result.stdout)
        assert masked.startswith(_EXPECTED_DATEFMT_SECTION)

    def test_no_stderr_output(_):
        result = _run_script()
        assert result.stderr == ""

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
