"""
cli-deed-plain_test.py

tests for the plain form of the `deed` CLI subcommand in `kamilog.py`
"""

import logging
import re

import pytest

from kamilog.kamilog import _DEEDS, _cli_parser

TIME = r"\d\d:\d\d:\d\d"


@pytest.fixture(autouse=True)
def _isolate_root_logger():
    """CLI logs on the root logger; restore it so other tests are unaffected"""
    root = logging.getLogger()
    saved = (root.handlers[:], root.filters[:], root.level)
    yield
    root.handlers[:], root.filters[:] = saved[0], saved[1]
    root.setLevel(saved[2])


def _run(argv, capsys):
    root = logging.getLogger()
    # pytest's own stream handlers would stop `getLogger` adding console ones
    root.handlers.clear()
    root.filters.clear()
    args = _cli_parser.parse_args(["deed", *argv])
    args.func(args)
    captured = capsys.readouterr()
    return captured.out, captured.err


class TestDeedPlainOutput:
    def test_create_file(_, capsys):
        out, _err = _run(["create-file", "out/a.txt", "--no-color"], capsys)
        assert re.fullmatch(TIME + r" INFO : create out/a.txt\n", out)

    def test_cp_file(_, capsys):
        argv = ["cp-file", "a.txt", "backup/a.txt", "--no-color"]
        out, _err = _run(argv, capsys)
        assert re.fullmatch(
            TIME + r" INFO : copy a.txt -> backup/a.txt\n", out
        )

    def test_omitted_trailing_argument(_, capsys):
        out, _err = _run(["download", "http://x/a", "--no-color"], capsys)
        assert out.rstrip().endswith("download http://x/a")

    def test_warning_goes_to_stderr(_, capsys):
        out, err = _run(["rm-file", "tmp/a.txt", "--no-color"], capsys)
        assert out == ""
        assert re.fullmatch(TIME + r" WARN\.: delete tmp/a.txt\n", err)

    def test_skip_level(_, capsys):
        out, _err = _run(["skip-file", "a", "--no-color"], capsys)
        assert "SKIP" in out and out.rstrip().endswith("skip a")

    @pytest.mark.parametrize("name", list(_DEEDS))
    def test_every_deed_has_subcommand(_, name, capsys):
        deed = _DEEDS[name]
        argv = [name.replace("_", "-"), *["x"] * len(deed.arg_names)]
        out, err = _run([*argv, "--no-color"], capsys)
        line = (out + err).rstrip()
        expected = deed.template.format(**dict.fromkeys(deed.arg_names, "x"))
        assert line.endswith(expected)


class TestDeedPlainLevel:
    def test_level_override(_, capsys):
        argv = ["cp-file", "a", "b", "--level", "note", "--no-color"]
        out, _err = _run(argv, capsys)
        assert re.fullmatch(TIME + r" NOTE : copy a -> b\n", out)

    def test_level_choice_is_lowercase_only(_, capsys):
        with pytest.raises(SystemExit):
            _run(["cp-file", "a", "b", "--level", "NOTE"], capsys)

    def test_unknown_level_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["cp-file", "a", "b", "--level", "bogus"], capsys)
        assert info.value.code == 2

    def test_debug_level_shows(_, capsys):
        argv = ["rm-file", "a", "--level", "debug", "--no-color"]
        out, _err = _run(argv, capsys)
        assert "DEBUG" in out


class TestDeedPlainParsing:
    def test_missing_subject_rejected(_, capsys):
        with pytest.raises(SystemExit) as info:
            _run(["cp-file"], capsys)
        assert info.value.code == 2

    def test_too_many_arguments_rejected(_, capsys):
        with pytest.raises(SystemExit):
            _run(["rm-file", "a", "b"], capsys)

    def test_unknown_deed_rejected(_, capsys):
        with pytest.raises(SystemExit):
            _run(["nope-file", "a"], capsys)

    def test_bare_deed_prints_help(_, capsys):
        out, _err = _run([], capsys)
        assert "create-file" in out and "cp-file" in out

    def test_no_color_has_no_escape(_, capsys):
        out, _err = _run(["create-file", "a", "--no-color"], capsys)
        assert "\x1b[" not in out
