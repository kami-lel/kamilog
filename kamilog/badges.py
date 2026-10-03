"""
badges: native badge table and badge normalization
"""

from .ansi import AnsiStyle

# native badge label → (hue, priority); higher priority prints earlier
_NATIVE_BADGES = {
    # mode
    "dry": (AnsiStyle.BRIGHT_MAGENTA, 73),
    "chk": (AnsiStyle.BRIGHT_BLUE, 68),
    "mock": (AnsiStyle.CYAN, 67),
    "sandbox": (AnsiStyle.BRIGHT_CYAN, 53),
    # guard
    "force": (AnsiStyle.BRIGHT_YELLOW, 84),
    "undo": (AnsiStyle.RED, 83),
    "grant": (AnsiStyle.BRIGHT_YELLOW, 66),
    "elevated": (AnsiStyle.BRIGHT_YELLOW, 93),
    "legacy": (AnsiStyle.YELLOW, 65),
    "unstable": (AnsiStyle.YELLOW, 72),
    # data
    "new": (AnsiStyle.BRIGHT_GREEN, 52),
    "owr": (AnsiStyle.RED, 64),
    "del": (AnsiStyle.RED, 82),
    "mv": (AnsiStyle.BRIGHT_GREEN, 47),
    "cp": (AnsiStyle.BRIGHT_GREEN, 46),
    "cached": (AnsiStyle.MAGENTA, 45),
    "stale": (AnsiStyle.YELLOW, 63),
    # automation
    "auto": (AnsiStyle.BLUE, 33),
    "fresh": (AnsiStyle.GREEN, 44),
    "resume": (AnsiStyle.GREEN, 43),
    "offline": (AnsiStyle.YELLOW, 42),
    # process
    "watch": (AnsiStyle.BRIGHT_BLUE, 32),
    "bg": (AnsiStyle.BLUE, 31),
    # recovery
    "retry": (AnsiStyle.BRIGHT_MAGENTA, 41),
    "fallback": (AnsiStyle.BRIGHT_YELLOW, 62),
    "timeout": (AnsiStyle.BRIGHT_RED, 81),
    "abort": (AnsiStyle.BRIGHT_RED, 92),
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
