"""
cb-zero-demo_test.py

golden test for `examples/cb/cb-zero_demo.py`; locks in its exact
stdout so future changes to CB0 rendering can't silently drift
"""

import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "cb"
    / "cb-zero_demo.py"
)

_EXPECTED = """\
Simple CB0:
####################
# Title
####################

Multi-line CB0:
##############################
# Section Title
# description line 1
# description line 2
##############################

Wide CB0 (custom width):
##################################################
# Feature Implementation
# Author: Development Team
# Status: In Progress
##################################################
"""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestCbZeroDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert result.stdout == _EXPECTED

    def test_no_stderr_output(_):
        result = _run_script()
        assert result.stderr == ""

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
