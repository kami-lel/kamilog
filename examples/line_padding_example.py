"""
line_padding_example.py

demonstrate all three line-padding functions printed to stdout
"""

import kamilog

print("# centered  " + "#" * 68)
kamilog.print_line_padding_centered("hello", "=")
kamilog.print_line_padding_centered("release v2.0", "*", line_width=40)
kamilog.print_line_padding_centered("done", "-", line_width=24)

print("\n# left justified  " + "#" * 62)
kamilog.print_line_padding_left_just("hello", "=")
kamilog.print_line_padding_left_just("release v2.0", ".", line_width=40)
kamilog.print_line_padding_left_just("done", "-", line_width=24)

print("\n# right justified  " + "#" * 61)
kamilog.print_line_padding_right_just("hello", "=")
kamilog.print_line_padding_right_just("release v2.0", ".", line_width=40)
kamilog.print_line_padding_right_just("done", "-", line_width=24)
