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
    renderer.color("CYAN", S.CYAN) + "\t\t\t"
    + renderer.color("BRIGHT_CYAN", S.BRIGHT_CYAN) + "\t\t"
    + renderer.color("BLUE", S.BLUE) + "\t\t\t"
    + renderer.color("BRIGHT_BLUE", S.BRIGHT_BLUE)
)
print(
    renderer.color("GREEN", S.GREEN) + "\t\t\t"
    + renderer.color("BRIGHT_GREEN", S.BRIGHT_GREEN) + "\t\t"
    + renderer.color("YELLOW", S.YELLOW) + "\t\t\t"
    + renderer.color("BRIGHT_YELLOW", S.BRIGHT_YELLOW)
)
print(
    renderer.color("RED", S.RED) + "\t\t\t"
    + renderer.color("BRIGHT_RED", S.BRIGHT_RED) + "\t\t"
    + renderer.color("BRIGHT_MAGENTA", S.BRIGHT_MAGENTA) + "\t\t"
    + renderer.color("GREY", S.GREY)
)

# backgrounds  ###################################################
print(kamilog.gen_comment_banner_centered(
    "backgrounds", 1, renderer=renderer
))
print(
    renderer.color("BG_CYAN", S.BG_CYAN) + "\t\t\t\t"
    + renderer.color("BG_BRIGHT_CYAN", S.BG_BRIGHT_CYAN) + "\t\t\t"
    + renderer.color("BG_BLUE", S.BG_BLUE) + "\t\t\t\t"
    + renderer.color("BG_BRIGHT_BLUE", S.BG_BRIGHT_BLUE)
)
print(
    renderer.color("BG_GREEN", S.BG_GREEN) + "\t\t\t"
    + renderer.color("BG_BRIGHT_GREEN", S.BG_BRIGHT_GREEN) + "\t\t\t"
    + renderer.color("BG_YELLOW", S.BG_YELLOW) + "\t\t\t"
    + renderer.color("BG_BRIGHT_YELLOW", S.BG_BRIGHT_YELLOW)
)
print(
    renderer.color("BG_RED", S.BG_RED) + "\t\t\t\t"
    + renderer.color("BG_BRIGHT_RED", S.BG_BRIGHT_RED) + "\t\t\t"
    + renderer.color("BG_BRIGHT_MAGENTA", S.BG_BRIGHT_MAGENTA) + "\t\t"
    + renderer.color("BG_GREY", S.BG_GREY)
)

# styles  #########################################################
print(kamilog.gen_comment_banner_centered("styles", 1, renderer=renderer))
print(renderer.color("bold", S.BOLD))
print(renderer.color("underline", S.UNDERLINE))

# combinations  ###################################################
print(kamilog.gen_comment_banner_centered(
    "combinations", 1, renderer=renderer
))
print(renderer.color(
    "The quick brown fox jumps over the lazy dog.",
    S.BOLD | S.UNDERLINE | S.RED | S.BG_YELLOW,
))
print(renderer.color(
    "Pack my box with five dozen liquor jugs.",
    S.BOLD | S.BRIGHT_GREEN | S.BG_BLUE,
))
