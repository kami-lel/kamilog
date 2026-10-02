"""
logger-deed-demo_test.py

golden-output test for `examples/logger/logger-deed_demo.py`: plain form,
track form on success and failure, the `act` handle, and `suppress`
"""

import os
import subprocess
import sys

import pytest

_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
_DEMO = os.path.join(_ROOT, "examples", "logger", "logger-deed_demo.py")

_EXPECTED_STDOUT = [
    "#################################  plain form  #################################",
    "INFO  deed: create out/a.txt",
    "INFO  deed: copy a.txt -> backup/a.txt",
    "INFO  deed: append out/a.txt",
    "INFO  deed: chmod run.sh 755",
    "INFO  deed: download https://example.com/a.zip",
    "INFO  deed: delete tmp/b.txt",
    "SKIP  deed: skip keep/a.txt",
    "INFO  dry\tdeed: copy a.txt -> backup/a.txt",
    "",
    "############################  track form: success  #############################",
    "INFO  deed: copy a.txt -> backup/a.txt",
    "DEBUG deed: run make",
    "",
    "############################  track form: failure  #############################",
    "the exception still propagated",
    "suppress carried on",
    "INFO  deed: fail to delete tmp/d.txt: OSError: already gone",
    "Traceback (most recent call last):",
    '  File "<DEMO>", line 63, in <module>',
    '    raise OSError("already gone")',
    "OSError: already gone",
    "",
    "#############################  track form: handle  #############################",
    "INFO  deed: download https://example.com/b.zip -> b.zip",
    "INFO  deed: download https://example.com/c.zip",
]

_EXPECTED_STDERR = [
    "WARN. deed: delete tmp/a.txt",
    "ERROR deed: fail to copy a.txt -> /root/a.txt: PermissionError: [Errno 13] Permission denied: '/root/a.txt'",
    "Traceback (most recent call last):",
    '  File "<DEMO>", line 52, in <module>',
    '    raise PermissionError(13, "Permission denied", "/root/a.txt")',
    "PermissionError: [Errno 13] Permission denied: '/root/a.txt'",
    "WARN. deed: fail to delete tmp/c.txt: OSError: device busy",
    "Traceback (most recent call last):",
    '  File "<DEMO>", line 57, in <module>',
    '    raise OSError("device busy")',
    "OSError: device busy",
    "ERROR deed: fail to run make: exit 2",
    "ERROR deed: fail to download https://example.com/d.zip: status 404",
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


def _normalize(text):
    """mask the machine-specific demo path, split lines"""
    text = text.replace(_DEMO, "<DEMO>")
    return text.split("\n")[:-1]


class TestDeedDemoOutput:
    _proc = _run_demo()
    _out_lines = _normalize(_proc.stdout)
    _err_lines = _normalize(_proc.stderr)

    def test_exits_cleanly(_):
        assert TestDeedDemoOutput._proc.returncode == 0

    def test_stdout_line_count(_):
        assert len(TestDeedDemoOutput._out_lines) == len(_EXPECTED_STDOUT)

    @pytest.mark.parametrize("i", range(len(_EXPECTED_STDOUT)))
    def test_stdout_line(_, i):
        assert TestDeedDemoOutput._out_lines[i] == _EXPECTED_STDOUT[i]

    def test_stderr_line_count(_):
        assert len(TestDeedDemoOutput._err_lines) == len(_EXPECTED_STDERR)

    @pytest.mark.parametrize("i", range(len(_EXPECTED_STDERR)))
    def test_stderr_line(_, i):
        assert TestDeedDemoOutput._err_lines[i] == _EXPECTED_STDERR[i]

    def test_no_stray_traceback_from_the_demo_itself(_):
        # 3 tracebacks in all: 1 on stdout (INFO), 2 on stderr
        tracebacks = TestDeedDemoOutput._out_lines + TestDeedDemoOutput._err_lines
        assert sum(ln.startswith("Traceback") for ln in tracebacks) == 3
