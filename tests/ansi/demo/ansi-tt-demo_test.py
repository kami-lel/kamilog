"""
ansi-tt-demo_test.py

golden-output test for `examples/ansi/ansi-tt-demo.py`, covering
`AnsiRenderer.color_triage_tag` and `gen_comment_banner_centered` in
`kamilog.py`
"""

import contextlib
import io

from kamilog import AnsiRenderer, gen_comment_banner_centered


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


def _run_demo():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        renderer = AnsiRenderer(_FakeStream(True))

        print(
            gen_comment_banner_centered("triage tags", 1, renderer=renderer)
        )
        print(
            renderer.color_triage_tag("BUG"),
            renderer.color_triage_tag("FIXME"),
            renderer.color_triage_tag("TODO"),
            renderer.color_triage_tag("HACK"),
            sep="\t",
        )
        print(
            renderer.color_triage_tag("Bug"),
            renderer.color_triage_tag("Fixme"),
            renderer.color_triage_tag("Todo"),
            renderer.color_triage_tag("Hack"),
            sep="\t",
        )
        print(
            renderer.color_triage_tag("bug"),
            renderer.color_triage_tag("fixme"),
            renderer.color_triage_tag("todo"),
            renderer.color_triage_tag("hack"),
            sep="\t",
        )

        print(
            gen_comment_banner_centered(
                "mock comments", 1, renderer=renderer
            )
        )
        print(
            "# " + renderer.color_triage_tag("TODO") + " implement data fetching"
        )
        print(
            "// " + renderer.color_triage_tag("Fixme") + " re-check array bounds"
        )
        print(
            "<!-- "
            + renderer.color_triage_tag("hack")
            + " workaround for old browsers -->"
        )
    return out.getvalue()


_EXPECTED = (
    "\033[90m" + "#" * 32 + "\033[0m"
    + "  triage tags  "
    + "\033[90m" + "#" * 33 + "\033[0m\n"
    + "\033[1;97;45mBUG\033[0m"
    + "\t\033[1;97;44mFIXME\033[0m"
    + "\t\033[1;30;43mTODO\033[0m"
    + "\t\033[1;30;46mHACK\033[0m\n"
    + "\033[30;105mBug\033[0m"
    + "\t\033[30;104mFixme\033[0m"
    + "\t\033[30;103mTodo\033[0m"
    + "\t\033[30;106mHack\033[0m\n"
    + "\033[35mbug\033[0m"
    + "\t\033[34mfixme\033[0m"
    + "\t\033[33mtodo\033[0m"
    + "\t\033[36mhack\033[0m\n"
    + "\033[90m" + "#" * 31 + "\033[0m"
    + "  mock comments  "
    + "\033[90m" + "#" * 32 + "\033[0m\n"
    + "# \033[1;30;43mTODO\033[0m implement data fetching\n"
    + "// \033[30;104mFixme\033[0m re-check array bounds\n"
    + "<!-- \033[36mhack\033[0m workaround for old browsers -->\n"
)


class TestAnsiTriageTagDemoOutput:
    def test_matches_golden_output(_):
        assert _run_demo() == _EXPECTED
