"""
line_padding_demo.py

demonstrate all three line-padding functions printed to stdout
"""

import sys

import kamilog

# repeated calls share one renderer instead of re-detecting TTY state
renderer = kamilog.AnsiRenderer(sys.stdout)

print("CENTERED")
print(kamilog.gen_line_padding_centered("hello", "=", renderer=renderer))
print(kamilog.gen_line_padding_centered(
    "release v2.0", "*", line_width=40, renderer=renderer
))
print(kamilog.gen_line_padding_centered(
    "done", "-", line_width=24, renderer=renderer
))

print("\nLEFT JUSTIFIED")
print(kamilog.gen_line_padding_left_just("hello", "=", renderer=renderer))
print(kamilog.gen_line_padding_left_just(
    "release v2.0", ".", line_width=40, renderer=renderer
))
print(kamilog.gen_line_padding_left_just(
    "done", "-", line_width=24, renderer=renderer
))

print("\nRIGHT JUSTIFIED")
print(kamilog.gen_line_padding_right_just("hello", "=", renderer=renderer))
print(kamilog.gen_line_padding_right_just(
    "release v2.0", ".", line_width=40, renderer=renderer
))
print(kamilog.gen_line_padding_right_just(
    "done", "-", line_width=24, renderer=renderer
))
