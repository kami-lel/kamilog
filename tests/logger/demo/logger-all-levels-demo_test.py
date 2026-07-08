"""
logger-all-levels-demo_test.py

golden test for `examples/logger/logger-all_levels_demo.py`; locks in
its exact stdout/stderr split so future changes to level routing or
padding can't silently drift
"""

import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "logger"
    / "logger-all_levels_demo.py"
)

_EXPECTED_STDOUT = """\
##############################  standard levels  ###############################
DEBUG: Debugging details here
INFO : Informational message

###############################  custom levels  ################################
ENTER: Starting database migration
SKIP : Skipped validation step
PASS : All assertions passed
SUCC.: User authentication succeeded
DONE : Migration completed successfully

###########################  all levels (in order)  ############################
DEBUG: Debugging information shown only during development
ENTER: Marks start of a routine
SKIP : Marks skipped portion of routine
SUCC.: Subroutine or execution succeeded
INFO : General informational message related to program function
PASS : Test case passed
DONE : Entire program or major component completed successfully
"""

_EXPECTED_STDERR = """\
WARN.: Warning message
ERROR: Error occurred
CRIT.: Critical issue
FAIL : Test case failed
WARN.: Warning condition that should be investigated
ERROR: Error condition that prevented operation completion
FAIL : Test case or subroutine/execution failed
CRIT.: Program stopping or crashing immediately
"""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestLoggerAllLevelsDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert result.stdout == _EXPECTED_STDOUT

    def test_stderr_matches_exactly(_):
        result = _run_script()
        assert result.stderr == _EXPECTED_STDERR

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
