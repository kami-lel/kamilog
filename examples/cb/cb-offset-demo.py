"""
cb-offset-demo.py

demonstrate horizontal_offset keeping a centered title aligned
across a bare banner and a context-prefixed one
"""

import sys

import kamilog

# repeated calls share one renderer instead of re-detecting TTY state
renderer = kamilog.AnsiRenderer(sys.stdout)

TITLE = "results"
PREFIX = "phase 2 "  # 8-char left context

# 1st line: plain centered banner across the full width
print(kamilog.gen_comment_banner_centered(
    TITLE, "=", line_width=80, renderer=renderer
))

# 2nd line: prefix eats 8 cols, so the banner spans the remaining 72;
# offset -4 (half the prefix) pulls Content back under the 1st title
print(PREFIX + kamilog.gen_comment_banner_centered(
    TITLE, "=", line_width=72, horizontal_offset=-4, renderer=renderer
))
