"""
logger-diff-only-stress-demo_test.py

golden test for `examples/logger/logger-diff_only_stress_demo.py`;
locks in its exact stdout (timestamps masked, since they vary by run)
across every word-boundary / leader / edge-case scenario so future
changes to diff-only compression can't silently drift
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "examples"
    / "logger"
    / "logger-diff_only_stress_demo.py"
)

_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


_EXPECTED_STDOUT = """\
########################  slash boundary — path prefix  ########################
<TIME> INFO  scan: scan /srv/data/archive/2024/q1/export/batch_001.csv ok
<TIME> INFO  scan: scan /srv/data/archive/2024/q1/export/batch_002.csv ok
<TIME> INFO  scan: scan /srv/data/archive/2024/q1/export/batch_003.csv ok
<TIME> INFO  scan: 	〃	〃	〃	〃	〃/batch_004.csv ok
<TIME> INFO  scan: 	〃	〃	〃	〃	〃/batch_005.csv ok
<TIME> INFO  scan: 	〃	〃	〃	〃	〃/batch_006.csv ok

##############  hyphen/underscore glue — kebab and snake tokens  ###############
<TIME> INFO  deploy: deploy target=prod  job=etl-run_011  ok
<TIME> INFO  deploy: deploy target=prod  job=etl-run_012  ok
<TIME> INFO  deploy: deploy target=prod  job=etl-run_013  ok
<TIME> INFO  deploy: 	〃	〃	〃    =etl-run_014  ok
<TIME> INFO  deploy: 	〃	〃	〃    =etl-run_015  ok
<TIME> INFO  deploy: 	〃	〃	〃    =etl-run_016  ok

#####################  equals boundary — key=value pairs  ######################
<TIME> INFO  sensor: sensor=cpu  temp=21.1C  humid=55%  st=ok
<TIME> INFO  sensor: sensor=cpu  temp=21.2C  humid=55%  st=ok
<TIME> INFO  sensor: sensor=cpu  temp=21.3C  humid=55%  st=ok
<TIME> INFO  sensor: 	〃	〃	〃.4〃	〃	〃  =ok
<TIME> INFO  sensor: 	〃	〃	〃.5〃	〃	〃  =ok
<TIME> INFO  sensor: 	〃	〃	〃.6〃	〃	〃  =ok

#####################  whitespace boundary — plain words  ######################
<TIME> INFO  poll: poll queue orders worker heartbeat seq 001
<TIME> INFO  poll: poll queue orders worker heartbeat seq 002
<TIME> INFO  poll: poll queue orders worker heartbeat seq 003
<TIME> INFO  poll: 	〃	〃	〃	〃	〃  004
<TIME> INFO  poll: 	〃	〃	〃	〃	〃  005
<TIME> INFO  poll: 	〃	〃	〃	〃	〃  006

#######################  2-tab fallback — unbroken hash  #######################
<TIME> INFO  csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392801
<TIME> INFO  csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392802
<TIME> INFO  csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392803
<TIME> INFO  csum: 	〃	〃	〃	〃	〃	09f8e7d6c5b4a392804
<TIME> INFO  csum: 	〃	〃	〃	〃	〃	09f8e7d6c5b4a392805
<TIME> INFO  csum: 	〃	〃	〃	〃	〃	09f8e7d6c5b4a392806

########################  short leader — bare tab jump  ########################
<TIME> INFO  pump: pump pressure stable flow steady cycle 1
<TIME> INFO  pump: pump pressure stable flow steady cycle 2
<TIME> INFO  pump: pump pressure stable flow steady cycle 3
<TIME> INFO  pump: 	〃	〃	〃	〃	〃  4
<TIME> INFO  pump: 	〃	〃	〃	〃	〃  5
<TIME> INFO  pump: 	〃	〃	〃	〃	〃  6

########################  long leader — leading marker  ########################
<TIME> INFO  telemetry: telemetry uplink nominal signal clear frame 1
<TIME> INFO  telemetry: telemetry uplink nominal signal clear frame 2
<TIME> INFO  telemetry: telemetry uplink nominal signal clear frame 3
<TIME> INFO  telemetry: 〃	〃	〃	〃	〃	〃    4
<TIME> INFO  telemetry: 〃	〃	〃	〃	〃	〃    5
<TIME> INFO  telemetry: 〃	〃	〃	〃	〃	〃    6

#######################  too short — nothing compressed  #######################
<TIME> INFO  up: up 7s node1 load 1.8
<TIME> INFO  up: up 14s node2 load 2.7
<TIME> INFO  up: up 21s node3 load 3.6
<TIME> INFO  up: up 28s node4 load 4.5
<TIME> INFO  up: up 35s node5 load 5.4
<TIME> INFO  up: up 42s node6 load 6.3

#####################  middle diff — common head and tail  #####################
<TIME> INFO  copy: copy file_001.tmp  to /var/backup/daily  ok
<TIME> INFO  copy: copy file_002.tmp  to /var/backup/daily  ok
<TIME> INFO  copy: copy file_003.tmp  to /var/backup/daily  ok
<TIME> INFO  copy: copy file_004〃	〃	〃	〃    ok
<TIME> INFO  copy: copy file_005〃	〃	〃	〃    ok
<TIME> INFO  copy: copy file_006〃	〃	〃	〃    ok

#####################  identical lines — full compression  #####################
<TIME> INFO  heartbeat: heartbeat gateway alive
<TIME> INFO  heartbeat: heartbeat gateway alive
<TIME> INFO  heartbeat: heartbeat gateway alive
<TIME> INFO  heartbeat: 〃	〃	〃  alive
<TIME> INFO  heartbeat: 〃	〃	〃  alive
<TIME> INFO  heartbeat: 〃	〃	〃  alive

"""

_EXPECTED_STDERR = ""


def _run_script():
    return subprocess.run(
        [sys.executable, str(_SCRIPT)], capture_output=True, text=True
    )


class TestLoggerDiffOnlyStressDemoOutput:
    def test_stdout_matches_exactly(_):
        result = _run_script()
        assert _mask_time(result.stdout) == _EXPECTED_STDOUT

    def test_no_stderr_output(_):
        result = _run_script()
        assert _mask_time(result.stderr) == _EXPECTED_STDERR

    def test_exits_successfully(_):
        result = _run_script()
        assert result.returncode == 0
