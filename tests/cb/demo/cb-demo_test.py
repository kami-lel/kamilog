"""
cb-demo_test.py

golden test for `examples/cb/cb-demo.py`; locks in its exact stdout so
future changes to the comment-banner functions can't silently drift
"""

import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent / "examples" / "cb" / "cb-demo.py"
)

_EXPECTED = """\
CENTERED
===================================  hello  ====================================
************  release v2.0  ************
--------  done  --------

LEFT JUSTIFIED
hello  =========================================================================
release v2.0  ..........................
done  ------------------

RIGHT JUSTIFIED
=========================================================================  hello
..........................  release v2.0
------------------  done
"""


def _run_script():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )
    return result


class TestCbDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert result.stdout == _EXPECTED

    def test_no_stderr_output(_):
        result = _run_script()
        assert result.stderr == ""

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
