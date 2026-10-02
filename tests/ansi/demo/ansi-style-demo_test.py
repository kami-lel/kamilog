"""
ansi-style-demo_test.py

golden-output test for `examples/ansi/ansi-style-demo.py`, covering
`AnsiStyle` flags and `AnsiRenderer.color` combinations in `kamilog`
"""

import contextlib
import io

from kamilog import AnsiRenderer, AnsiStyle, gen_comment_banner_centered


class _FakeStream:
    def __init__(self, is_tty):
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


def _run_demo():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        renderer = AnsiRenderer(_FakeStream(True))
        S = AnsiStyle

        print(gen_comment_banner_centered("colors", 1, renderer=renderer))
        print(
            renderer.color("RED", S.RED)
            + "\t\t"
            + renderer.color("BRIGHT_RED", S.BRIGHT_RED)
            + "\t\t"
            + renderer.color("YELLOW", S.YELLOW)
            + "\t\t"
            + renderer.color("BRIGHT_YELLOW", S.BRIGHT_YELLOW)
        )
        print(
            renderer.color("GREEN", S.GREEN)
            + "\t\t"
            + renderer.color("BRIGHT_GREEN", S.BRIGHT_GREEN)
            + "\t\t"
            + renderer.color("CYAN", S.CYAN)
            + "\t\t"
            + renderer.color("BRIGHT_CYAN", S.BRIGHT_CYAN)
        )
        print(
            renderer.color("BLUE", S.BLUE)
            + "\t\t"
            + renderer.color("BRIGHT_BLUE", S.BRIGHT_BLUE)
            + "\t\t"
            + renderer.color("MAGENTA", S.MAGENTA)
            + "\t\t"
            + renderer.color("BRIGHT_MAGENTA", S.BRIGHT_MAGENTA)
        )
        print(
            renderer.color("BLACK", S.BLACK)
            + "\t\t"
            + renderer.color("GREY", S.GREY)
            + "\t\t\t"
            + renderer.color("WHITE", S.WHITE)
            + "\t\t"
            + renderer.color("BRIGHT_WHITE", S.BRIGHT_WHITE)
        )

        print(
            gen_comment_banner_centered("backgrounds", 1, renderer=renderer)
        )
        print(
            renderer.color("BG_RED", S.BG_RED)
            + "\t\t"
            + renderer.color("BG_BRIGHT_RED", S.BG_BRIGHT_RED)
            + "\t\t"
            + renderer.color("BG_YELLOW", S.BG_YELLOW)
            + "\t"
            + renderer.color("BG_BRIGHT_YELLOW", S.BG_BRIGHT_YELLOW)
        )
        print(
            renderer.color("BG_GREEN", S.BG_GREEN)
            + "\t"
            + renderer.color("BG_BRIGHT_GREEN", S.BG_BRIGHT_GREEN)
            + "\t\t"
            + renderer.color("BG_CYAN", S.BG_CYAN)
            + "\t\t"
            + renderer.color("BG_BRIGHT_CYAN", S.BG_BRIGHT_CYAN)
        )
        print(
            renderer.color("BG_BLUE", S.BG_BLUE)
            + "\t\t"
            + renderer.color("BG_BRIGHT_BLUE", S.BG_BRIGHT_BLUE)
            + "\t\t"
            + renderer.color("BG_MAGENTA", S.BG_MAGENTA)
            + "\t"
            + renderer.color("BG_BRIGHT_MAGENTA", S.BG_BRIGHT_MAGENTA)
        )
        print(
            renderer.color("BG_BLACK", S.BG_BLACK)
            + "\t"
            + renderer.color("BG_GREY", S.BG_GREY)
            + "\t\t\t"
            + renderer.color("BG_WHITE", S.BG_WHITE)
            + "\t"
            + renderer.color("BG_BRIGHT_WHITE", S.BG_BRIGHT_WHITE)
        )

        print(gen_comment_banner_centered("styles", 1, renderer=renderer))
        print(renderer.color("bold", S.BOLD))
        print(renderer.color("underline", S.UNDERLINE))

        print(
            gen_comment_banner_centered("combinations", 1, renderer=renderer)
        )
        print(
            renderer.color(
                "bold + underline + red-on-yellow",
                S.BOLD | S.UNDERLINE | S.RED | S.BG_YELLOW,
            )
        )
        print(
            renderer.color(
                "bold + bright_green-on-blue",
                S.BOLD | S.BRIGHT_GREEN | S.BG_BLUE,
            )
        )
    return out.getvalue()


def _grey(fill):
    return "\033[90m" + fill + "\033[0m"


_EXPECTED = (
    _grey("#" * 35) + "  colors  " + _grey("#" * 35) + "\n"
    + "\033[31mRED\033[0m"
    + "\t\t\033[91mBRIGHT_RED\033[0m"
    + "\t\t\033[33mYELLOW\033[0m"
    + "\t\t\033[93mBRIGHT_YELLOW\033[0m\n"
    + "\033[32mGREEN\033[0m"
    + "\t\t\033[92mBRIGHT_GREEN\033[0m"
    + "\t\t\033[36mCYAN\033[0m"
    + "\t\t\033[96mBRIGHT_CYAN\033[0m\n"
    + "\033[34mBLUE\033[0m"
    + "\t\t\033[94mBRIGHT_BLUE\033[0m"
    + "\t\t\033[35mMAGENTA\033[0m"
    + "\t\t\033[95mBRIGHT_MAGENTA\033[0m\n"
    + "\033[30mBLACK\033[0m"
    + "\t\t\033[90mGREY\033[0m"
    + "\t\t\t\033[37mWHITE\033[0m"
    + "\t\t\033[97mBRIGHT_WHITE\033[0m\n"
    + _grey("#" * 32) + "  backgrounds  " + _grey("#" * 33) + "\n"
    + "\033[41mBG_RED\033[0m"
    + "\t\t\033[101mBG_BRIGHT_RED\033[0m"
    + "\t\t\033[43mBG_YELLOW\033[0m"
    + "\t\033[103mBG_BRIGHT_YELLOW\033[0m\n"
    + "\033[42mBG_GREEN\033[0m"
    + "\t\033[102mBG_BRIGHT_GREEN\033[0m"
    + "\t\t\033[46mBG_CYAN\033[0m"
    + "\t\t\033[106mBG_BRIGHT_CYAN\033[0m\n"
    + "\033[44mBG_BLUE\033[0m"
    + "\t\t\033[104mBG_BRIGHT_BLUE\033[0m"
    + "\t\t\033[45mBG_MAGENTA\033[0m"
    + "\t\033[105mBG_BRIGHT_MAGENTA\033[0m\n"
    + "\033[40mBG_BLACK\033[0m"
    + "\t\033[100mBG_GREY\033[0m"
    + "\t\t\t\033[47mBG_WHITE\033[0m"
    + "\t\033[107mBG_BRIGHT_WHITE\033[0m\n"
    + _grey("#" * 35) + "  styles  " + _grey("#" * 35) + "\n"
    + "\033[1mbold\033[0m\n"
    + "\033[4munderline\033[0m\n"
    + _grey("#" * 32) + "  combinations  " + _grey("#" * 32) + "\n"
    + "\033[1;4;31;43mbold + underline + red-on-yellow\033[0m\n"
    + "\033[1;92;44mbold + bright_green-on-blue\033[0m\n"
)


class TestAnsiStyleDemoOutput:
    def test_matches_golden_output(_):
        assert _run_demo() == _EXPECTED
