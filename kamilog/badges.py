"""
badges: native badge table and badge normalization
"""

from .ansi import AnsiStyle

# native badge label → (hue, priority); higher priority prints earlier
_NATIVE_BADGES = {
    "dry": (AnsiStyle.BRIGHT_YELLOW, 45),
    "chk": (AnsiStyle.YELLOW, 44),
    "mock": (AnsiStyle.YELLOW, 43),
    "sbx": (AnsiStyle.GREEN, 33),
    "force": (AnsiStyle.RED, 52),
    "undo": (AnsiStyle.RED, 51),
    "unsafe": (AnsiStyle.BRIGHT_RED, 53),
    "yes": (AnsiStyle.YELLOW, 42),
    "auto": (AnsiStyle.BLUE, 13),
    "strict": (AnsiStyle.GREEN, 32),
    "keep": (AnsiStyle.YELLOW, 41),
    "fast": (AnsiStyle.GREEN, 31),
    "retries": (AnsiStyle.CYAN, 25),
    "resm": (AnsiStyle.CYAN, 24),
    "new": (AnsiStyle.CYAN, 23),
    "offl": (AnsiStyle.CYAN, 22),
    "incr": (AnsiStyle.CYAN, 21),
    "watch": (AnsiStyle.BLUE, 12),
    "bg": (AnsiStyle.BLUE, 11),
}


def _normalize_badges(badges):
    """
    drop duplicate badges, then order by descending priority;
    customs rank 0 and keep the order given
    """
    if badges is None:
        return ()
    if isinstance(badges, str):
        badges = (badges,)
    unique = tuple(dict.fromkeys(badges))
    return tuple(
        sorted(unique, key=lambda b: -_NATIVE_BADGES.get(b, (None, 0))[1])
    )
