"""
ansi-style-demo.py

demonstrate `AnsiStyle` flags and `AnsiRenderer.color` combinations
"""

import sys

import kamilog

renderer = kamilog.AnsiRenderer(sys.stdout)
S = kamilog.AnsiStyle

# colors  ########################################################
print(kamilog.gen_comment_banner_centered("colors", 1, renderer=renderer))
print(
    renderer.color("CYAN", S.CYAN)
    + "\t\t"
    + renderer.color("BRIGHT_CYAN", S.BRIGHT_CYAN)
    + "\t\t"
    + renderer.color("BLUE", S.BLUE)
    + "\t\t"
    + renderer.color("BRIGHT_BLUE", S.BRIGHT_BLUE)
)
print(
    renderer.color("GREEN", S.GREEN)
    + "\t\t"
    + renderer.color("BRIGHT_GREEN", S.BRIGHT_GREEN)
    + "\t\t"
    + renderer.color("YELLOW", S.YELLOW)
    + "\t\t"
    + renderer.color("BRIGHT_YELLOW", S.BRIGHT_YELLOW)
)
print(
    renderer.color("RED", S.RED)
    + "\t\t"
    + renderer.color("BRIGHT_RED", S.BRIGHT_RED)
    + "\t\t"
    + renderer.color("MAGENTA", S.MAGENTA)
    + "\t\t"
    + renderer.color("BRIGHT_MAGENTA", S.BRIGHT_MAGENTA)
)
print(
    renderer.color("BLACK", S.BLACK)
    + "\t\t"
    + renderer.color("GREY", S.GREY)
    + "\t\t"
    + renderer.color("WHITE", S.WHITE)
    + "\t\t"
    + renderer.color("BRIGHT_WHITE", S.BRIGHT_WHITE)
)

# backgrounds  ###################################################
print(kamilog.gen_comment_banner_centered("backgrounds", 1, renderer=renderer))
print(
    renderer.color("BG_CYAN", S.BG_CYAN)
    + "\t\t"
    + renderer.color("BG_BRIGHT_CYAN", S.BG_BRIGHT_CYAN)
    + "\t\t"
    + renderer.color("BG_BLUE", S.BG_BLUE)
    + "\t\t"
    + renderer.color("BG_BRIGHT_BLUE", S.BG_BRIGHT_BLUE)
)
print(
    renderer.color("BG_GREEN", S.BG_GREEN)
    + "\t"
    + renderer.color("BG_BRIGHT_GREEN", S.BG_BRIGHT_GREEN)
    + "\t\t"
    + renderer.color("BG_YELLOW", S.BG_YELLOW)
    + "\t"
    + renderer.color("BG_BRIGHT_YELLOW", S.BG_BRIGHT_YELLOW)
)
print(
    renderer.color("BG_RED", S.BG_RED)
    + "\t\t"
    + renderer.color("BG_BRIGHT_RED", S.BG_BRIGHT_RED)
    + "\t\t"
    + renderer.color("BG_MAGENTA", S.BG_MAGENTA)
    + "\t"
    + renderer.color("BG_BRIGHT_MAGENTA", S.BG_BRIGHT_MAGENTA)
)
print(
    renderer.color("BG_BLACK", S.BG_BLACK)
    + "\t\t"
    + renderer.color("BG_GREY", S.BG_GREY)
    + "\t\t"
    + renderer.color("BG_WHITE", S.BG_WHITE)
    + "\t\t"
    + renderer.color("BG_BRIGHT_WHITE", S.BG_BRIGHT_WHITE)
)

# styles  #########################################################
print(kamilog.gen_comment_banner_centered("styles", 1, renderer=renderer))
print(renderer.color("bold", S.BOLD))
print(renderer.color("underline", S.UNDERLINE))

# combinations  ###################################################
print(kamilog.gen_comment_banner_centered("combinations", 1, renderer=renderer))
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
