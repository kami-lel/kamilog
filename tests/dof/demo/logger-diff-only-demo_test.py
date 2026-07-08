"""
logger-diff-only-demo_test.py

golden test for `examples/logger/logger-diff_only_demo.py`; locks in
its exact stdout/stderr (timestamps masked, since they vary by run) so
future changes to diff-only compression can't silently drift
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "logger"
    / "logger-diff_only_demo.py"
)

_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


_EXPECTED_STDOUT = """\
#############################  basic compression  ##############################
<TIME> INFO  sensor: sensor=cpu  load=45.2%  temp=61C  ok
<TIME> INFO  sensor: sensor=cpu  load=47.8%  temp=62C  ok
<TIME> INFO  sensor: sensor=cpu  load=44.1%  temp=60C  ok
<TIME> INFO  sensor: \t〃\t〃     =51.3%  temp=63C  ok
<TIME> INFO  sensor: \t〃\t〃     =49.7%  temp=62C  ok
<TIME> INFO  sensor: \t〃\t〃     =53.0%  temp=64C  ok

#########################  pattern break and recovery  #########################
<TIME> INFO  sync: sync /home/alice/docs/q1_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: sync /home/alice/docs/q2_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: sync /home/alice/docs/q3_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: \t〃\t〃\t〃/q4\t〃\t〃\t〃\t〃  ok
<TIME> INFO  sync: \t〃\t〃\t〃/q5\t〃\t〃\t〃\t〃  ok
-------------------------  outlier poisons the window  -------------------------
<TIME> INFO  sync: sync /home/alice/docs/q6_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: sync /home/alice/docs/q7_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: sync /home/alice/docs/q8_report.pdf  →  remote:backup  ok
<TIME> INFO  sync: \t〃\t〃\t〃/q9\t〃\t〃\t〃\t〃  ok
"""

_EXPECTED_STDERR = """\
<TIME> WARN. sync: WARN disk 91 full on remote:backup — sync paused
"""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestLoggerDiffOnlyDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert _mask_time(result.stdout) == _EXPECTED_STDOUT

    def test_stderr_matches_exactly(_):
        result = _run_script()
        assert _mask_time(result.stderr) == _EXPECTED_STDERR

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
