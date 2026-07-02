"""
cb-number-demo.py

demonstrate numeric padding shortcuts (1-5) for comment-banner functions
"""

import sys

import kamilog

# numeric padding shortcuts: 1→#, 2→=, 3→*, 4→+, 5→-
renderer = kamilog.AnsiRenderer(sys.stdout)

for padding in range(1, 6):
    print(
        kamilog.gen_comment_banner_centered(
            "title", padding, renderer=renderer
        )
    )
