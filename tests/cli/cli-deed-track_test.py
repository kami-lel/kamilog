"""
cli-deed-track_test.py

tests for the track form (`-- COMMAND`) of the `deed` CLI subcommand in
`kamilog.py`
"""

import logging
import re
import sys

import pytest

from kamilog.kamilog import _cli_parser

OK = [sys.executable, "-c", "pass"]
EXIT_3 = [sys.executable, "-c", "raise SystemExit(3)"]


@pytest.fixture(autouse=True)
def _isolate_root_logger():
    """CLI logs on the root logger; restore it so other tests are unaffected"""
    root = logging.getLogger()
    saved = (root.handlers[:], root.filters[:], root.level)
    yield
    root.handlers[:], root.filters[:] = saved[0], saved[1]
    root.setLevel(saved[2])


def _run(argv, capsys):
    """run the CLI; return (status, stdout, stderr) of its own logging"""
    root = logging.getLogger()
    # pytest's own stream handlers would stop `getLogger` adding console ones
    root.handlers.clear()
    root.filters.clear()
    args = _cli_parser.parse_args(["deed", *argv])
    status = args.func(args)
    captured = capsys.readouterr()
    return status, captured.out, captured.err


class TestDeedTrackSuccess:
    def test_status_zero_logs_success(_, capsys):
        status, out, _err = _run(
            ["cp-file", "a.txt", "backup/a.txt", "--no-color", "--", *OK],
            capsys,
        )
        assert status == 0
        assert re.fullmatch(
            r"INFO : copy a.txt -> backup/a.txt\n", out
        )

    def test_level_override_on_success(_, capsys):
        _status, out, _err = _run(
            ["rm-file", "a", "--level", "debug", "--no-color", "--", *OK],
            capsys,
        )
        assert re.fullmatch(r"DEBUG: delete a\n", out)

    def test_command_runs_after_parse_only_once(_, capsys, tmp_path):
        marker = tmp_path / "count.txt"
        cmd = [
            sys.executable,
            "-c",
            "open({!r}, 'a').write('x')".format(str(marker)),
        ]
        _run(["create-file", "a", "--", *cmd], capsys)
        assert marker.read_text() == "x"


class TestDeedTrackFailure:
    def test_nonzero_status_logs_failure_and_returns_it(_, capsys):
        status, out, err = _run(
            ["cp-file", "a", "b", "--no-color", "--", *EXIT_3], capsys
        )
        assert status == 3
        assert out == ""
        assert re.fullmatch(
            r"ERROR: fail to copy a -> b: exit 3\n", err
        )

    def test_no_traceback(_, capsys):
        _status, _out, err = _run(["rm-file", "a", "--", *EXIT_3], capsys)
        assert "Traceback" not in err

    def test_err_level_override(_, capsys):
        _status, _out, err = _run(
            ["cp-file", "a", "b", "--err-level", "warning", "--no-color",
             "--", *EXIT_3],
            capsys,
        )
        assert re.fullmatch(
            r"WARN\.: fail to copy a -> b: exit 3\n", err
        )

    def test_level_does_not_touch_failure_line(_, capsys):
        _status, _out, err = _run(
            ["cp-file", "a", "b", "--level", "debug", "--no-color",
             "--", *EXIT_3],
            capsys,
        )
        assert "ERROR" in err

    def test_default_err_level_follows_deed(_, capsys):
        _status, _out, err = _run(
            ["rm-file", "a", "--no-color", "--", *EXIT_3], capsys
        )
        assert "WARN." in err

    def test_missing_program_is_127(_, capsys):
        status, _out, err = _run(
            ["run-command", "--no-color", "--", "/no/such/program-xyz"],
            capsys,
        )
        assert status == 127
        assert "FileNotFoundError" in err

    def test_signal_death_maps_to_shell_status(_, capsys):
        cmd = [
            sys.executable,
            "-c",
            "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
        ]
        status, _out, _err = _run(["run-command", "--", *cmd], capsys)
        assert status == 128 + 15


class TestDeedTrackRunCommand:
    def test_wrapped_command_is_subject(_, capsys):
        status, out, _err = _run(
            ["run-command", "--no-color", "--", sys.executable, "-c", "pass"],
            capsys,
        )
        assert status == 0
        assert out.rstrip().endswith("run {} -c pass".format(sys.executable))

    def test_failure_names_command_once(_, capsys):
        _status, _out, err = _run(
            ["run-command", "--no-color", "--", *EXIT_3], capsys
        )
        assert err.count("SystemExit(3)") == 1
        assert err.rstrip().endswith("exit 3")

    def test_arguments_with_spaces_are_quoted(_, capsys):
        _status, out, _err = _run(
            ["run-command", "--no-color", "--", sys.executable, "-c",
             "pass # a b"],
            capsys,
        )
        assert "'pass # a b'" in out

    def test_repeating_command_before_dashes_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["run-command", "make", "--", *OK], capsys)
        assert info.value.code == 2

    def test_plain_form_still_takes_positional_command(_, capsys):
        status, out, _err = _run(["run-command", "make", "--no-color"], capsys)
        assert status == 0
        assert out.rstrip().endswith("run make")

    def test_plain_form_without_command_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["run-command"], capsys)
        assert info.value.code == 2


class TestDeedTrackParsing:
    def test_err_level_without_command_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["rm-file", "a", "--err-level", "error"], capsys)
        assert info.value.code == 2

    def test_empty_command_after_dashes_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["create-file", "a", "--"], capsys)
        assert info.value.code == 2

    def test_unknown_err_level_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["rm-file", "a", "--err-level", "bogus", "--", *OK], capsys)
        assert info.value.code == 2

    def test_options_after_dashes_belong_to_command(_, capsys):
        status, out, _err = _run(
            ["run-command", "--no-color", "--", sys.executable, "-c", "pass",
             "--level", "debug"],
            capsys,
        )
        assert status == 0 and "INFO" in out

    def test_other_subcommands_unaffected_by_dashes(_):
        args = _cli_parser.parse_args(["cb", "c", "=", "-w", "20"])
        assert not hasattr(args, "tail_command")
