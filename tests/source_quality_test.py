"""
Tests for source code quality markers in kamilog source files.
"""

import re
from pathlib import Path

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


def test_kamilog_py_no_banned_markers():
    v = _violations(_KAMILOG_DIR / "kamilog.py")
    assert not v, _fmt(v)


def test_init_py_no_banned_markers():
    v = _violations(_KAMILOG_DIR / "__init__.py")
    assert not v, _fmt(v)
