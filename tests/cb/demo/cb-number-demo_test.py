"""
cb-number-demo_test.py

golden test for `examples/cb/cb-number-demo.py`; locks in its exact
stdout so future changes to numeric padding shortcuts can't silently
drift
"""

import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "cb"
    / "cb-number-demo.py"
)

_EXPECTED = """\
###################################  title  ####################################
===================================  title  ====================================
***********************************  title  ************************************
+++++++++++++++++++++++++++++++++++  title  ++++++++++++++++++++++++++++++++++++
-----------------------------------  title  ------------------------------------
"""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestCbNumberDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert result.stdout == _EXPECTED

    def test_no_stderr_output(_):
        result = _run_script()
        assert result.stderr == ""

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
