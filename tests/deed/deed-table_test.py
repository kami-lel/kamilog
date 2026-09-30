"""
deed-table_test.py

tests for `_DEEDS` and `_render_deed_message` in `kamilog.py`
"""

import re
from pathlib import Path

import pytest

from kamilog.kamilog import (
    _DEEDS,
    _render_deed_message,
    ERROR,
    INFO,
    SKIP,
    WARNING,
)

DOC_PATH = Path(__file__).parents[2] / "docs" / "deed-doc.md"

EXPECTED_ORDER = (
    "create_file",
    "owr_file",
    "cp_file",
    "mv_file",
    "rm_file",
    "create_dir",
    "rm_dir",
    "pack_files",
    "unpack_archive",
    "download",
    "upload",
    "run_command",
    "load_config",
    "save_config",
    "skip_file",
)


def _read_doc_tables(heading):
    """tables after `heading`, each as rows of cells without header & rule"""
    text = DOC_PATH.read_text(encoding="utf-8")
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    tables, rows = [], []
    for line in section.splitlines() + [""]:
        if line.startswith("|"):
            cells = line.strip("|").split("|")
            rows.append([c.strip().strip("`") for c in cells])
        elif rows:
            tables.append(rows[2:])  # header & rule
            rows = []
    return tables


class TestDeedTable:
    def test_fifteen_deeds_in_doc_order(_):
        assert tuple(_DEEDS) == EXPECTED_ORDER

    def test_name_matches_key(_):
        for key, deed in _DEEDS.items():
            assert deed.name == key

    def test_arg_names_match_template_fields(_):
        for deed in _DEEDS.values():
            fields = tuple(re.findall(r"\{(\w+)\}", deed.template))
            assert fields == deed.arg_names

    def test_args_and_templates_match_doc_deeds_table(_):
        rows = _read_doc_tables("\n## Deeds")[0]
        assert [r[0] for r in rows] == list(EXPECTED_ORDER)
        for name, arg_names, remark in rows:
            assert _DEEDS[name].arg_names == tuple(arg_names.split(", "))
            assert _DEEDS[name].template == remark

    def test_levels_match_doc_levels_table(_):
        by_label = {
            "INFO": INFO,
            "WARNING": WARNING,
            "ERROR": ERROR,
            "SKIP": SKIP,
        }
        rows = _read_doc_tables("\n## Deeds")[1]
        assert [r[0] for r in rows] == list(EXPECTED_ORDER)
        for name, level, err_level in rows:
            assert _DEEDS[name].level == by_label[level]
            assert _DEEDS[name].err_level == by_label[err_level]


class TestRenderDeedMessage:
    @pytest.mark.parametrize(
        "name, args, expected",
        [
            ("create_file", ("out/a.txt",), "create out/a.txt"),
            ("owr_file", ("out/a.txt",), "overwrite out/a.txt"),
            ("cp_file", ("a", "b"), "copy a -> b"),
            ("mv_file", ("a", "b"), "move a -> b"),
            ("rm_file", ("a",), "delete a"),
            ("create_dir", ("d",), "create dir d"),
            ("rm_dir", ("d",), "delete dir d"),
            ("pack_files", ("src", "a.tgz"), "pack src -> a.tgz"),
            ("unpack_archive", ("a.tgz", "out"), "unpack a.tgz -> out"),
            ("download", ("http://x/a", "a"), "download http://x/a -> a"),
            ("upload", ("a", "http://x"), "upload a -> http://x"),
            ("run_command", ("make",), "run make"),
            ("load_config", ("c.toml",), "load c.toml"),
            ("save_config", ("c.toml",), "save c.toml"),
            ("skip_file", ("a",), "skip a"),
        ],
    )
    def test_full_args(_, name, args, expected):
        assert _render_deed_message(_DEEDS[name], *args) == expected

    @pytest.mark.parametrize(
        "name, args, expected",
        [
            ("cp_file", ("a",), "copy a"),
            ("mv_file", ("a",), "move a"),
            ("pack_files", ("src",), "pack src"),
            ("unpack_archive", ("a.tgz",), "unpack a.tgz"),
            ("download", ("http://x/a",), "download http://x/a"),
            ("upload", ("a",), "upload a"),
        ],
    )
    def test_omitted_trailing_destination(_, name, args, expected):
        assert _render_deed_message(_DEEDS[name], *args) == expected

    def test_all_omitted_leaves_verb(_):
        assert _render_deed_message(_DEEDS["cp_file"]) == "copy"
        assert _render_deed_message(_DEEDS["create_dir"]) == "create dir"

    def test_omitted_leading_arg_keeps_later_segment(_):
        got = _render_deed_message(_DEEDS["cp_file"], destination="b")
        assert got == "copy -> b"

    def test_named_args(_):
        got = _render_deed_message(
            _DEEDS["cp_file"], source="a", destination="b"
        )
        assert got == "copy a -> b"

    def test_none_counts_as_omitted(_):
        assert _render_deed_message(_DEEDS["cp_file"], "a", None) == "copy a"

    def test_non_str_args_stringified(_):
        assert _render_deed_message(_DEEDS["rm_file"], Path("x")) == "delete x"

    def test_too_many_args_rejected(_):
        with pytest.raises(TypeError):
            _render_deed_message(_DEEDS["rm_file"], "a", "b")

    def test_unknown_or_duplicate_named_arg_rejected(_):
        with pytest.raises(TypeError):
            _render_deed_message(_DEEDS["rm_file"], nope="a")
        with pytest.raises(TypeError):
            _render_deed_message(_DEEDS["rm_file"], "a", path="b")
