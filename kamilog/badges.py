"""
badges: native badge table and badge normalization
"""

from .ansi import AnsiStyle

# native badge label → (hue, priority); higher priority prints earlier
_NATIVE_BADGES = {
    # mode
    "dry": (AnsiStyle.BRIGHT_YELLOW, 73),
    "chk": (AnsiStyle.YELLOW, 68),
    "mock": (AnsiStyle.YELLOW, 67),
    "sandbox": (AnsiStyle.GREEN, 53),
    # guard
    "force": (AnsiStyle.RED, 84),
    "undo": (AnsiStyle.RED, 83),
    "grant": (AnsiStyle.YELLOW, 66),
    "elevated": (AnsiStyle.BRIGHT_RED, 93),
    "legacy": (AnsiStyle.YELLOW, 65),
    "unstable": (AnsiStyle.BRIGHT_YELLOW, 72),
    # data
    "new": (AnsiStyle.GREEN, 52),
    "owr": (AnsiStyle.YELLOW, 64),
    "del": (AnsiStyle.RED, 82),
    "mv": (AnsiStyle.CYAN, 47),
    "cp": (AnsiStyle.CYAN, 46),
    "cached": (AnsiStyle.CYAN, 45),
    "stale": (AnsiStyle.YELLOW, 63),
    # automation
    "auto": (AnsiStyle.BLUE, 33),
    "fresh": (AnsiStyle.CYAN, 44),
    "resume": (AnsiStyle.CYAN, 43),
    "offline": (AnsiStyle.CYAN, 42),
    # process
    "watch": (AnsiStyle.BLUE, 32),
    "bg": (AnsiStyle.BLUE, 31),
    # recovery
    "retry": (AnsiStyle.CYAN, 41),
    "fallback": (AnsiStyle.YELLOW, 62),
    "timeout": (AnsiStyle.RED, 81),
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
