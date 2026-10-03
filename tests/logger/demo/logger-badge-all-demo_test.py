"""
logger-badge-all-demo_test.py

golden-output test for `examples/logger/logger-badge-all_demo.py`: every
native badge plus a custom one, one per log entry, grouped by category
"""

import os
import subprocess
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DEMO = os.path.join(_ROOT, "examples", "logger", "logger-badge-all_demo.py")

_EXPECTED_STDOUT = [
    "####################################  mode  ####################################",
    "INFO  dry\t: reporting only, nothing modified",
    "INFO  chk\t: validating input, nothing modified",
    "INFO  mock\t: hitting stand-in payment gateway",
    "INFO  sandbox\t: running isolated, nothing outlives it",
    "",
    "###################################  guard  ####################################",
    "INFO  force\t: bypassing the lock file check",
    "INFO  undo\t: reverting the previous migration",
    "INFO  grant\t: granting write access to the shared bucket",
    "INFO  elevated\t: running with superuser rights",
    "INFO  legacy\t: calling the deprecated v1 endpoint",
    "INFO  unstable\t: using the experimental scheduler",
    "",
    "####################################  data  ####################################",
    "INFO  new\t: creating output/report.csv",
    "INFO  owr\t: overwriting output/report.csv",
    "INFO  del\t: deleting output/report.csv",
    "INFO  mv\t: renaming draft.csv to report.csv",
    "INFO  cp\t: duplicating report.csv to report.bak",
    "INFO  cached\t: serving report.csv from cache",
    "INFO  stale\t: serving report.csv older than expected",
    "",
    "#################################  automation  #################################",
    "INFO  auto\t: unattended run, auto-answering prompts",
    "INFO  fresh\t: ignoring previous state, starting over",
    "INFO  resume\t: continuing the interrupted run",
    "INFO  offline\t: running without network, cached data only",
    "",
    "##################################  process  ###################################",
    "INFO  watch\t: re-running on file change",
    "INFO  bg\t: running detached from the terminal",
    "",
    "##################################  recovery  ##################################",
    "INFO  retry\t: repeating the failed upload",
    "INFO  fallback\t: taking the secondary path after primary failed",
    "INFO  skip\t: skipping the broken validation step",
    "INFO  timeout\t: hitting the 30 second time limit",
    "INFO  abort\t: cutting the run short on purpose",
    "",
    "###################################  custom  ###################################",
    "INFO  eu-west\t: pushing to the eu-west region",
]


def _run_demo():
    env = dict(os.environ, PYTHONPATH=_ROOT)
    return subprocess.run(
        [sys.executable, _DEMO],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


class TestBadgeAllDemoOutput:
    _proc = _run_demo()
    _out_lines = _proc.stdout.split("\n")[:-1]

    def test_exits_cleanly_with_no_stderr(_):
        assert TestBadgeAllDemoOutput._proc.returncode == 0
        assert TestBadgeAllDemoOutput._proc.stderr == ""

    def test_line_count(_):
        assert len(TestBadgeAllDemoOutput._out_lines) == len(_EXPECTED_STDOUT)

    @pytest.mark.parametrize("i", range(len(_EXPECTED_STDOUT)))
    def test_stdout_line(_, i):
        assert TestBadgeAllDemoOutput._out_lines[i] == _EXPECTED_STDOUT[i]

    def test_covers_every_native_badge_exactly_once(_):
        from kamilog.badges import _NATIVE_BADGES

        seen = [
            line.split("\t", 1)[0].split("  ", 1)[1]
            for line in TestBadgeAllDemoOutput._out_lines
            if line.startswith("INFO  ") and "eu-west" not in line
        ]
        assert sorted(seen) == sorted(_NATIVE_BADGES)
        assert len(seen) == len(set(seen))
