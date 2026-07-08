"""
ansi-tt-demo.py

demonstrate `AnsiRenderer.color_triage_tag` across all 12 triage tags
"""

import sys

import kamilog

renderer = kamilog.AnsiRenderer(sys.stdout)

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
