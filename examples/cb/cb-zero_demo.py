"""
cb-zero_demo.py

demonstrate CB0 (multi-line boxed comment banner) with various content
"""

import sys

import kamilog

# repeated calls share one renderer instead of re-detecting TTY state
renderer = kamilog.AnsiRenderer(sys.stdout)

print("Simple CB0:")
lines = ["Title"]
print(kamilog.gen_comment_banner_zero(lines, line_width=20, renderer=renderer))

print("\nMulti-line CB0:")
lines = [
    "Section Title",
    "description line 1",
    "description line 2",
]
print(kamilog.gen_comment_banner_zero(lines, line_width=30, renderer=renderer))

print("\nWide CB0 (custom width):")
lines = [
    "Feature Implementation",
    "Author: Development Team",
    "Status: In Progress",
]
print(
    kamilog.gen_comment_banner_zero(
        lines, line_width=50, renderer=renderer
    )
)
