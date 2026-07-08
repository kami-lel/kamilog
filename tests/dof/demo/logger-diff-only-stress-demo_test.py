"""
logger-diff-only-stress-demo_test.py

tests for `_DiffOnlyMsgFilter` across word-boundary, leader, and
edge-case scenarios in `kamilog.py`; each scenario logs 6 lines: 3
warmup, then 3 compressed
"""

import contextlib
import io
import re

import pytest

import kamilog

_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")


def _mask_time(text):
    return _TIME_RE.sub("<TIME>", text)


def _run_and_capture(name, messages):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        log = kamilog.getLogger(name)
        log.setLevel(kamilog.DEBUG)
        log.propagate = False
        for message in messages:
            log.info(message)
    return _mask_time(out.getvalue()), _mask_time(err.getvalue())


# slash boundary  ###############################################################
# cut lands on "/": directory head compressed, "/file" tail printed intact

_SLASH_BOUNDARY_MESSAGES = [
    "scan /srv/data/archive/2024/q1/export/batch_00{}.csv ok".format(i)
    for i in range(1, 7)
]
_SLASH_BOUNDARY_STDOUT = [
    "<TIME> INFO  stress-demo-scan: scan /srv/data/archive/2024/q1/export/batch_001.csv ok",
    "<TIME> INFO  stress-demo-scan: scan /srv/data/archive/2024/q1/export/batch_002.csv ok",
    "<TIME> INFO  stress-demo-scan: scan /srv/data/archive/2024/q1/export/batch_003.csv ok",
    "<TIME> INFO  stress-demo-scan: 〃\t〃\t〃\t〃\t〃    /batch_004.csv ok",
    "<TIME> INFO  stress-demo-scan: 〃\t〃\t〃\t〃\t〃    /batch_005.csv ok",
    "<TIME> INFO  stress-demo-scan: 〃\t〃\t〃\t〃\t〃    /batch_006.csv ok",
]


class TestSlashBoundaryPathPrefix:
    _out, _err = _run_and_capture("stress-demo-scan", _SLASH_BOUNDARY_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestSlashBoundaryPathPrefix._err == ""

    @pytest.mark.parametrize("i", range(len(_SLASH_BOUNDARY_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestSlashBoundaryPathPrefix._out_lines[i]
            == _SLASH_BOUNDARY_STDOUT[i]
        )


# hyphen and underscore glue  ###################################################
# "-" and "_" are word chars: token cut falls back to the "=" before it

_HYPHEN_UNDERSCORE_MESSAGES = [
    "deploy target=prod  job=etl-run_01{}  ok".format(i) for i in range(1, 7)
]
_HYPHEN_UNDERSCORE_STDOUT = [
    "<TIME> INFO  stress-demo-deploy: deploy target=prod  job=etl-run_011  ok",
    "<TIME> INFO  stress-demo-deploy: deploy target=prod  job=etl-run_012  ok",
    "<TIME> INFO  stress-demo-deploy: deploy target=prod  job=etl-run_013  ok",
    "<TIME> INFO  stress-demo-deploy: 〃\t〃\t〃\t〃=etl-run_014  ok",
    "<TIME> INFO  stress-demo-deploy: 〃\t〃\t〃\t〃=etl-run_015  ok",
    "<TIME> INFO  stress-demo-deploy: 〃\t〃\t〃\t〃=etl-run_016  ok",
]


class TestHyphenUnderscoreGlue:
    _out, _err = _run_and_capture("stress-demo-deploy", _HYPHEN_UNDERSCORE_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestHyphenUnderscoreGlue._err == ""

    @pytest.mark.parametrize("i", range(len(_HYPHEN_UNDERSCORE_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestHyphenUnderscoreGlue._out_lines[i]
            == _HYPHEN_UNDERSCORE_STDOUT[i]
        )


# equals boundary  ###############################################################
# key=value pairs: cut lands on "=", key compressed, "=value" printed

_EQUALS_BOUNDARY_MESSAGES = [
    "sensor=cpu  temp=21.{}C  humid=55%  st=ok".format(i) for i in range(1, 7)
]
_EQUALS_BOUNDARY_STDOUT = [
    "<TIME> INFO  stress-demo-sensor: sensor=cpu  temp=21.1C  humid=55%  st=ok",
    "<TIME> INFO  stress-demo-sensor: sensor=cpu  temp=21.2C  humid=55%  st=ok",
    "<TIME> INFO  stress-demo-sensor: sensor=cpu  temp=21.3C  humid=55%  st=ok",
    "<TIME> INFO  stress-demo-sensor: 〃\t〃\t〃    .4〃\t〃\t=ok",
    "<TIME> INFO  stress-demo-sensor: 〃\t〃\t〃    .5〃\t〃\t=ok",
    "<TIME> INFO  stress-demo-sensor: 〃\t〃\t〃    .6〃\t〃\t=ok",
]


class TestEqualsBoundaryKeyValuePairs:
    _out, _err = _run_and_capture("stress-demo-sensor", _EQUALS_BOUNDARY_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestEqualsBoundaryKeyValuePairs._err == ""

    @pytest.mark.parametrize("i", range(len(_EQUALS_BOUNDARY_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestEqualsBoundaryKeyValuePairs._out_lines[i]
            == _EQUALS_BOUNDARY_STDOUT[i]
        )


# whitespace boundary  ###########################################################
# plain words: cut lands on the space before the changing field

_WHITESPACE_BOUNDARY_MESSAGES = [
    "poll queue orders worker heartbeat seq {:03d}".format(i) for i in range(1, 7)
]
_WHITESPACE_BOUNDARY_STDOUT = [
    "<TIME> INFO  stress-demo-poll: poll queue orders worker heartbeat seq 001",
    "<TIME> INFO  stress-demo-poll: poll queue orders worker heartbeat seq 002",
    "<TIME> INFO  stress-demo-poll: poll queue orders worker heartbeat seq 003",
    "<TIME> INFO  stress-demo-poll: 〃\t〃\t〃\t〃\t〃      004",
    "<TIME> INFO  stress-demo-poll: 〃\t〃\t〃\t〃\t〃      005",
    "<TIME> INFO  stress-demo-poll: 〃\t〃\t〃\t〃\t〃      006",
]


class TestWhitespaceBoundaryPlainWords:
    _out, _err = _run_and_capture("stress-demo-poll", _WHITESPACE_BOUNDARY_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestWhitespaceBoundaryPlainWords._err == ""

    @pytest.mark.parametrize("i", range(len(_WHITESPACE_BOUNDARY_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestWhitespaceBoundaryPlainWords._out_lines[i]
            == _WHITESPACE_BOUNDARY_STDOUT[i]
        )


# 2-tab fallback  ################################################################
# unbroken hex token longer than 2 tab stops: mid-word tab-aligned cut

_TWO_TAB_FALLBACK_MESSAGES = [
    "csum sha256"
    ":9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a3928{:02x}".format(i)
    for i in range(1, 7)
]
_TWO_TAB_FALLBACK_STDOUT = [
    "<TIME> INFO  stress-demo-csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392801",
    "<TIME> INFO  stress-demo-csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392802",
    "<TIME> INFO  stress-demo-csum: csum sha256:9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a392803",
    "<TIME> INFO  stress-demo-csum: 〃\t〃\t〃\t〃\t〃\t2b1a09f8e7d6c5b4a392804",
    "<TIME> INFO  stress-demo-csum: 〃\t〃\t〃\t〃\t〃\t2b1a09f8e7d6c5b4a392805",
    "<TIME> INFO  stress-demo-csum: 〃\t〃\t〃\t〃\t〃\t2b1a09f8e7d6c5b4a392806",
]


class TestTwoTabFallbackUnbrokenHash:
    _out, _err = _run_and_capture("stress-demo-csum", _TWO_TAB_FALLBACK_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestTwoTabFallbackUnbrokenHash._err == ""

    @pytest.mark.parametrize("i", range(len(_TWO_TAB_FALLBACK_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestTwoTabFallbackUnbrokenHash._out_lines[i]
            == _TWO_TAB_FALLBACK_STDOUT[i]
        )


# short leader  ##################################################################
# run start sits < 4 columns before a tab stop: leader becomes a bare tab jump

_SHORT_LEADER_MESSAGES = [
    "pump pressure stable flow steady cycle {}".format(i) for i in range(1, 7)
]
_SHORT_LEADER_STDOUT = [
    "<TIME> INFO  stress-demo-pump: pump pressure stable flow steady cycle 1",
    "<TIME> INFO  stress-demo-pump: pump pressure stable flow steady cycle 2",
    "<TIME> INFO  stress-demo-pump: pump pressure stable flow steady cycle 3",
    "<TIME> INFO  stress-demo-pump: 〃\t〃\t〃\t〃\t〃      4",
    "<TIME> INFO  stress-demo-pump: 〃\t〃\t〃\t〃\t〃      5",
    "<TIME> INFO  stress-demo-pump: 〃\t〃\t〃\t〃\t〃      6",
]


class TestShortLeaderBareTabJump:
    _out, _err = _run_and_capture("stress-demo-pump", _SHORT_LEADER_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestShortLeaderBareTabJump._err == ""

    @pytest.mark.parametrize("i", range(len(_SHORT_LEADER_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestShortLeaderBareTabJump._out_lines[i]
            == _SHORT_LEADER_STDOUT[i]
        )


# long leader  ###################################################################
# run start sits >= 4 columns before a tab stop: leader earns its own marker

_LONG_LEADER_MESSAGES = [
    "telemetry uplink nominal signal clear frame {}".format(i) for i in range(1, 7)
]
_LONG_LEADER_STDOUT = [
    "<TIME> INFO  stress-demo-telemetry: telemetry uplink nominal signal clear frame 1",
    "<TIME> INFO  stress-demo-telemetry: telemetry uplink nominal signal clear frame 2",
    "<TIME> INFO  stress-demo-telemetry: telemetry uplink nominal signal clear frame 3",
    "<TIME> INFO  stress-demo-telemetry: \t〃\t〃\t〃\t〃\t〃\t  4",
    "<TIME> INFO  stress-demo-telemetry: \t〃\t〃\t〃\t〃\t〃\t  5",
    "<TIME> INFO  stress-demo-telemetry: \t〃\t〃\t〃\t〃\t〃\t  6",
]


class TestLongLeaderLeadingMarker:
    _out, _err = _run_and_capture("stress-demo-telemetry", _LONG_LEADER_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestLongLeaderLeadingMarker._err == ""

    @pytest.mark.parametrize("i", range(len(_LONG_LEADER_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestLongLeaderLeadingMarker._out_lines[i]
            == _LONG_LEADER_STDOUT[i]
        )


# too short to compress  #########################################################
# common runs shorter than one marker block: lines print untouched

_TOO_SHORT_MESSAGES = [
    "up {}s node{} load {}.{}".format(i * 7, i, i, 9 - i) for i in range(1, 7)
]
_TOO_SHORT_STDOUT = [
    "<TIME> INFO  stress-demo-up: up 7s node1 load 1.8",
    "<TIME> INFO  stress-demo-up: up 14s node2 load 2.7",
    "<TIME> INFO  stress-demo-up: up 21s node3 load 3.6",
    "<TIME> INFO  stress-demo-up: up 28s node4 load 4.5",
    "<TIME> INFO  stress-demo-up: up 35s node5 load 5.4",
    "<TIME> INFO  stress-demo-up: up 42s node6 load 6.3",
]


class TestTooShortNothingCompressed:
    _out, _err = _run_and_capture("stress-demo-up", _TOO_SHORT_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestTooShortNothingCompressed._err == ""

    @pytest.mark.parametrize("i", range(len(_TOO_SHORT_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestTooShortNothingCompressed._out_lines[i]
            == _TOO_SHORT_STDOUT[i]
        )


# middle diff, common tail  ######################################################
# change sits mid-line: head and tail runs compress around it

_MIDDLE_DIFF_MESSAGES = [
    "copy file_{:03d}.tmp  to /var/backup/daily  ok".format(i) for i in range(1, 7)
]
_MIDDLE_DIFF_STDOUT = [
    "<TIME> INFO  stress-demo-copy: copy file_001.tmp  to /var/backup/daily  ok",
    "<TIME> INFO  stress-demo-copy: copy file_002.tmp  to /var/backup/daily  ok",
    "<TIME> INFO  stress-demo-copy: copy file_003.tmp  to /var/backup/daily  ok",
    "<TIME> INFO  stress-demo-copy: copy file_004\t〃\t〃\t〃\t  ok",
    "<TIME> INFO  stress-demo-copy: copy file_005\t〃\t〃\t〃\t  ok",
    "<TIME> INFO  stress-demo-copy: copy file_006\t〃\t〃\t〃\t  ok",
]


class TestMiddleDiffCommonHeadAndTail:
    _out, _err = _run_and_capture("stress-demo-copy", _MIDDLE_DIFF_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestMiddleDiffCommonHeadAndTail._err == ""

    @pytest.mark.parametrize("i", range(len(_MIDDLE_DIFF_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestMiddleDiffCommonHeadAndTail._out_lines[i]
            == _MIDDLE_DIFF_STDOUT[i]
        )


# identical lines  ###############################################################
# whole message common: everything up to the last word compresses

_IDENTICAL_LINES_MESSAGES = ["heartbeat gateway alive"] * 6
_IDENTICAL_LINES_STDOUT = [
    "<TIME> INFO  stress-demo-heartbeat: heartbeat gateway alive",
    "<TIME> INFO  stress-demo-heartbeat: heartbeat gateway alive",
    "<TIME> INFO  stress-demo-heartbeat: heartbeat gateway alive",
    "<TIME> INFO  stress-demo-heartbeat: \t〃\t〃      alive",
    "<TIME> INFO  stress-demo-heartbeat: \t〃\t〃      alive",
    "<TIME> INFO  stress-demo-heartbeat: \t〃\t〃      alive",
]


class TestIdenticalLinesFullCompression:
    _out, _err = _run_and_capture("stress-demo-heartbeat", _IDENTICAL_LINES_MESSAGES)
    _out_lines = _out.splitlines()

    def test_no_stderr(_):
        assert TestIdenticalLinesFullCompression._err == ""

    @pytest.mark.parametrize("i", range(len(_IDENTICAL_LINES_STDOUT)))
    def test_stdout_line(_, i):
        assert (
            TestIdenticalLinesFullCompression._out_lines[i]
            == _IDENTICAL_LINES_STDOUT[i]
        )
