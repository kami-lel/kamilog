"""
logger-badge-demo_test.py

golden-output test for `examples/logger/logger-badge_demo.py`: operation
badges, per-line compression of a multi-line message, and space-separated
dittos on a long line
"""

import os
import re
import subprocess
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DEMO = os.path.join(_ROOT, "examples", "logger", "logger-badge_demo.py")
_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")

_EXPECTED_STDOUT = [
    "##############################  run-wide badges  ###############################",
    "<TIME> DONE  copy: wrote a.txt",
    "<TIME> DONE \tdry yes\tcopy: wrote b.txt",
    "<TIME> DONE \tdry yes deploy\tcopy: wrote c.txt",
    "<TIME> DONE  copy: wrote d.txt",
    "<TIME> DONE  copy: wrote e.txt",
    "",
    "#########################  badges keep dittos aligned  #########################",
    "<TIME> INFO \tforce dry auto\tsync: sync /home/alice/docs/q1_report.pdf  ->  remote:backup  ok",
    "<TIME> INFO \tforce dry auto\tsync: sync /home/alice/docs/q2_report.pdf  ->  remote:backup  ok",
    "<TIME> INFO \tforce dry auto\tsync: sync /home/alice/docs/q3_report.pdf  ->  remote:backup  ok",
    "<TIME> INFO \tforce dry auto\tsync: \t〃\t〃\t〃 /q4\t〃\t〃\t〃\t〃    ok",
    "<TIME> INFO \tforce dry auto\tsync: \t〃\t〃\t〃 /q5\t〃\t〃\t〃\t〃    ok",
    "",
    "#############################  multi-line message  #############################",
    "<TIME> INFO \tdry\tbuild: compile /src/module_1.c  ok",
    "link    /out/module_1.o  ok",
    "<TIME> INFO \tdry\tbuild: compile /src/module_2.c  ok",
    "link    /out/module_2.o  ok",
    "<TIME> INFO \tdry\tbuild: compile /src/module_3.c  ok",
    "link    /out/module_3.o  ok",
    "<TIME> INFO \tdry\tbuild: \t〃\t〃 /module_4.c  ok",
    "〃\t〃  /module_4.o  ok",
    "<TIME> INFO \tdry\tbuild: \t〃\t〃 /module_5.c  ok",
    "〃\t〃  /module_5.o  ok",
    "",
    "#################################  long line  ##################################",
    "<TIME> INFO \tchk\tscan: scan /var/data/archive/2026/09/shard_1/records.dat  checksum=ok  size=1048576  owner=backup  mode=0640  path=/mnt/nas/shard_1",
    "<TIME> INFO \tchk\tscan: scan /var/data/archive/2026/09/shard_2/records.dat  checksum=ok  size=1048576  owner=backup  mode=0640  path=/mnt/nas/shard_2",
    "<TIME> INFO \tchk\tscan: scan /var/data/archive/2026/09/shard_3/records.dat  checksum=ok  size=1048576  owner=backup  mode=0640  path=/mnt/nas/shard_3",
    "<TIME> INFO \tchk\tscan: 〃 〃 〃 〃 /shard_4〃 〃 〃 〃 〃 〃 〃 〃 〃 〃 〃 /shard_4",
    "<TIME> INFO \tchk\tscan: 〃 〃 〃 〃 /shard_5〃 〃 〃 〃 〃 〃 〃 〃 〃 〃 〃 /shard_5",
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


class TestBadgeDemoOutput:
    _proc = _run_demo()
    _out_lines = _TIME_RE.sub("<TIME>", _proc.stdout).split("\n")[:-1]

    def test_exits_cleanly_with_no_stderr(_):
        assert TestBadgeDemoOutput._proc.returncode == 0
        assert TestBadgeDemoOutput._proc.stderr == ""

    def test_line_count(_):
        assert len(TestBadgeDemoOutput._out_lines) == len(_EXPECTED_STDOUT)

    @pytest.mark.parametrize("i", range(len(_EXPECTED_STDOUT)))
    def test_stdout_line(_, i):
        assert TestBadgeDemoOutput._out_lines[i] == _EXPECTED_STDOUT[i]

    def test_long_line_dittos_carry_no_tabs_after_the_source(_):
        long_lines = [
            line
            for line in TestBadgeDemoOutput._out_lines
            if line.startswith("<TIME> INFO \tchk\tscan: 〃")
        ]
        assert len(long_lines) == 2
        tails = [line.split("scan: ", 1)[1] for line in long_lines]
        assert all("\t" not in tail for tail in tails)
