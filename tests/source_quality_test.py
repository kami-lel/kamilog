"""
Tests for source code quality markers in kamilog source files.
"""

import re
from pathlib import Path

import pytest

_KAMILOG_DIR = Path(__file__).parent.parent / "kamilog"
_BANNED = re.compile(r"\b(todo|bug|fixme|hack)\b", re.IGNORECASE)
_STRING_LITERAL = re.compile(r"\"[^\"]*\"|'[^']*'")


def _violations(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        (i + 1, line)
        for i, line in enumerate(lines)
        if _BANNED.search(_STRING_LITERAL.sub("", line))
    ]


def _fmt(violations):
    return "\n".join(
        "  line {}: {}".format(lineno, line.strip())
        for lineno, line in violations
    )


@pytest.mark.parametrize(
    "path", sorted(_KAMILOG_DIR.glob("*.py")), ids=lambda p: p.name
)
def test_source_no_banned_markers(path):
    v = _violations(path)
    assert not v, _fmt(v)
