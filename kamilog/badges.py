"""
badges: native badge table and badge normalization
"""

from .ansi import AnsiStyle

# native badge label → hue
NATIVE_BADGES = {
    # mode
    "dry": AnsiStyle.BRIGHT_MAGENTA,
    "chk": AnsiStyle.BRIGHT_BLUE,
    "mock": AnsiStyle.CYAN,
    "sandbox": AnsiStyle.BRIGHT_CYAN,
    # guard
    "force": AnsiStyle.BRIGHT_YELLOW,
    "undo": AnsiStyle.RED,
    "grant": AnsiStyle.BRIGHT_YELLOW,
    "elevated": AnsiStyle.BRIGHT_YELLOW,
    "legacy": AnsiStyle.YELLOW,
    "unstable": AnsiStyle.YELLOW,
    # data
    "new": AnsiStyle.BRIGHT_GREEN,
    "edit": AnsiStyle.BRIGHT_GREEN,
    "owr": AnsiStyle.RED,
    "del": AnsiStyle.RED,
    "mv": AnsiStyle.BRIGHT_GREEN,
    "cp": AnsiStyle.BRIGHT_GREEN,
    "cached": AnsiStyle.MAGENTA,
    "stale": AnsiStyle.YELLOW,
    # automation
    "auto": AnsiStyle.BLUE,
    "fresh": AnsiStyle.GREEN,
    "resume": AnsiStyle.GREEN,
    "offline": AnsiStyle.YELLOW,
    # process
    "watch": AnsiStyle.BRIGHT_BLUE,
    "bg": AnsiStyle.BLUE,
    # recovery
    "retry": AnsiStyle.BRIGHT_MAGENTA,
    "fallback": AnsiStyle.BRIGHT_YELLOW,
    "timeout": AnsiStyle.BRIGHT_RED,
    "abort": AnsiStyle.BRIGHT_RED,
}


def normalize_badges(badges):
    """
    drop duplicate badges, keeping the order given
    """
    if badges is None:
        return ()
    if isinstance(badges, str):
        badges = (badges,)
    return tuple(dict.fromkeys(badges))
