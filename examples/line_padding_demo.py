"""
line_padding_demo.py

demonstrate all three line-padding functions printed to stdout
"""

import kamilog

print("CENTERED")
kamilog.print_line_padding_centered("hello", "=")
kamilog.print_line_padding_centered("release v2.0", "*", line_width=40)
kamilog.print_line_padding_centered("done", "-", line_width=24)

print("\nLEFT JUSTIFIED")
kamilog.print_line_padding_left_just("hello", "=")
kamilog.print_line_padding_left_just("release v2.0", ".", line_width=40)
kamilog.print_line_padding_left_just("done", "-", line_width=24)

print("\nRIGHT JUSTIFIED")
kamilog.print_line_padding_right_just("hello", "=")
kamilog.print_line_padding_right_just("release v2.0", ".", line_width=40)
kamilog.print_line_padding_right_just("done", "-", line_width=24)
