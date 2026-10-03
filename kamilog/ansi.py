"""
ANSI color: the combinable ``AnsiStyle`` flag and the TTY-aware
``AnsiRenderer``
"""

import logging
from enum import Flag, auto

from .levels import _CustomLogLevel


class AnsiStyle(Flag):  # =====================================================
    """
    style/foreground/background flags, combinable via ``|``;
    values carry no ANSI meaning, q.v. ``AnsiRenderer._ANSI_STYLE2CODE``
    for the code lookup
    """

    # foreground color  --------------------------------------------------------

    RED = auto()
    BRIGHT_RED = auto()
    YELLOW = auto()
    BRIGHT_YELLOW = auto()
    GREEN = auto()
    BRIGHT_GREEN = auto()
    CYAN = auto()
    BRIGHT_CYAN = auto()
    BLUE = auto()
    BRIGHT_BLUE = auto()
    MAGENTA = auto()
    BRIGHT_MAGENTA = auto()

    BLACK = auto()
    GREY = auto()
    WHITE = auto()
    BRIGHT_WHITE = auto()

    # background color  --------------------------------------------------------

    BG_RED = auto()
    BG_BRIGHT_RED = auto()
    BG_YELLOW = auto()
    BG_BRIGHT_YELLOW = auto()
    BG_GREEN = auto()
    BG_BRIGHT_GREEN = auto()
    BG_CYAN = auto()
    BG_BRIGHT_CYAN = auto()
    BG_BLUE = auto()
    BG_BRIGHT_BLUE = auto()
    BG_MAGENTA = auto()
    BG_BRIGHT_MAGENTA = auto()

    BG_BLACK = auto()
    BG_GREY = auto()
    BG_WHITE = auto()
    BG_BRIGHT_WHITE = auto()

    # style  -------------------------------------------------------------------

    BOLD = auto()
    UNDERLINE = auto()

    # Public API  **************************************************************

    @classmethod
    def parse(cls, raw):
        """
        parse a comma-separated list of ``AnsiStyle`` member names into a
        single combined ``AnsiStyle`` value


        :param raw: comma-separated member names, eg ``"RED,BOLD"``
        :type raw: str
        :raises ValueError: ``raw`` contains an unknown member name
        :return: combined style
        :rtype: AnsiStyle
        """
        style = cls(0)
        for name in raw.split(","):
            name = name.strip().upper()
            try:
                style |= cls[name]
            except KeyError:
                raise ValueError("unknown AnsiStyle member {!r}".format(name))
        return style


class AnsiRenderer:  # =========================================================
    """
    TTY-aware ANSI color code renderer, detects TTY status at construction


    :param stream: output stream used for TTY detection;
            ``None`` disables color unconditionally
    :type stream: IO or None
    :param is_disabled: whether to disable color unconditionally,
            regardless of ``stream``; default=False
    :type is_disabled: bool, optional
    """

    _RESET = "\033[0m"

    _ANSI_STYLE2CODE = {
        AnsiStyle.BOLD: "1",
        AnsiStyle.UNDERLINE: "4",
        AnsiStyle.RED: "31",
        AnsiStyle.BRIGHT_RED: "91",
        AnsiStyle.YELLOW: "33",
        AnsiStyle.BRIGHT_YELLOW: "93",
        AnsiStyle.GREEN: "32",
        AnsiStyle.BRIGHT_GREEN: "92",
        AnsiStyle.CYAN: "36",
        AnsiStyle.BRIGHT_CYAN: "96",
        AnsiStyle.BLUE: "34",
        AnsiStyle.BRIGHT_BLUE: "94",
        AnsiStyle.MAGENTA: "35",
        AnsiStyle.BRIGHT_MAGENTA: "95",
        AnsiStyle.BLACK: "30",
        AnsiStyle.GREY: "90",
        AnsiStyle.WHITE: "37",
        AnsiStyle.BRIGHT_WHITE: "97",
        AnsiStyle.BG_RED: "41",
        AnsiStyle.BG_BRIGHT_RED: "101",
        AnsiStyle.BG_YELLOW: "43",
        AnsiStyle.BG_BRIGHT_YELLOW: "103",
        AnsiStyle.BG_GREEN: "42",
        AnsiStyle.BG_BRIGHT_GREEN: "102",
        AnsiStyle.BG_CYAN: "46",
        AnsiStyle.BG_BRIGHT_CYAN: "106",
        AnsiStyle.BG_BLUE: "44",
        AnsiStyle.BG_BRIGHT_BLUE: "104",
        AnsiStyle.BG_MAGENTA: "45",
        AnsiStyle.BG_BRIGHT_MAGENTA: "105",
        AnsiStyle.BG_BLACK: "40",
        AnsiStyle.BG_GREY: "100",
        AnsiStyle.BG_WHITE: "47",
        AnsiStyle.BG_BRIGHT_WHITE: "107",
    }

    _LEVEL2ANSI_COLOR = {
        logging.DEBUG: AnsiStyle.CYAN,
        _CustomLogLevel.ENTER: AnsiStyle.BRIGHT_CYAN,
        _CustomLogLevel.SKIP: AnsiStyle.BRIGHT_CYAN,
        _CustomLogLevel.SUCC: AnsiStyle.BRIGHT_GREEN,
        logging.INFO: AnsiStyle.BLUE,
        _CustomLogLevel.PASS: AnsiStyle.GREEN,
        _CustomLogLevel.NOTE: AnsiStyle.BRIGHT_BLUE,
        _CustomLogLevel.TIP: AnsiStyle.BRIGHT_BLUE,
        _CustomLogLevel.DONE: AnsiStyle.BRIGHT_GREEN,
        _CustomLogLevel.HINT: AnsiStyle.MAGENTA,
        _CustomLogLevel.IMPORTANT: AnsiStyle.BRIGHT_MAGENTA,
        logging.WARNING: AnsiStyle.YELLOW,
        _CustomLogLevel.CAUTION: AnsiStyle.YELLOW,
        logging.ERROR: AnsiStyle.BRIGHT_YELLOW,
        _CustomLogLevel.FAIL: AnsiStyle.RED,
        logging.CRITICAL: AnsiStyle.BRIGHT_RED,
    }

    _TRIAGE_TAG2ANSI_STYLE = {
        "BUG": AnsiStyle.BRIGHT_WHITE | AnsiStyle.BG_MAGENTA | AnsiStyle.BOLD,
        "Bug": AnsiStyle.BLACK | AnsiStyle.BG_BRIGHT_MAGENTA,
        "bug": AnsiStyle.MAGENTA,
        "FIXME": AnsiStyle.BRIGHT_WHITE | AnsiStyle.BG_BLUE | AnsiStyle.BOLD,
        "Fixme": AnsiStyle.BLACK | AnsiStyle.BG_BRIGHT_BLUE,
        "fixme": AnsiStyle.BLUE,
        "HACK": AnsiStyle.BLACK | AnsiStyle.BG_CYAN | AnsiStyle.BOLD,
        "Hack": AnsiStyle.BLACK | AnsiStyle.BG_BRIGHT_CYAN,
        "hack": AnsiStyle.CYAN,
        "TODO": AnsiStyle.BLACK | AnsiStyle.BG_YELLOW | AnsiStyle.BOLD,
        "Todo": AnsiStyle.BLACK | AnsiStyle.BG_BRIGHT_YELLOW,
        "todo": AnsiStyle.YELLOW,
    }

    def __init__(self, stream=None, *, is_disabled=False):
        self._enabled = (
            not is_disabled
            and stream is not None
            and hasattr(stream, "isatty")
            and stream.isatty()
        )

    # Public API  **************************************************************

    def color(self, text, style):
        """
        apply ANSI style codes to text


        :param text: text to colorize
        :type text: str
        :param style: ANSI style to apply, combine flags with ``|``,
                eg ``AnsiStyle.BOLD | AnsiStyle.RED | AnsiStyle.BG_YELLOW``
        :type style: AnsiStyle
        :return: ``text`` with style applied if color is enabled;
                otherwise ``text`` unchanged
        :rtype: str
        """
        if not self._enabled:
            return text

        codes = [
            code
            for flag, code in self._ANSI_STYLE2CODE.items()
            if flag in style
        ]
        return "\033[{}m{}{}".format(";".join(codes), text, self._RESET)

    def color_grey(self, text):
        """
        apply bright-black (grey) ANSI color to ``text``


        :param text: text to colorize
        :type text: str
        :return: ``text`` in grey if color is enabled; otherwise unchanged
        :rtype: str
        """
        return self.color(text, AnsiStyle.GREY)

    def color_level(self, text, levelno):
        """
        apply bold and level-specific ANSI color to ``text``


        :param text: text to colorize
        :type text: str
        :param levelno: numeric log level used to select the color
        :type levelno: int
        :return: ``text`` with the level's style applied if color is enabled
                and the level is known; otherwise ``text`` unchanged
        :rtype: str
        """
        color = self._LEVEL2ANSI_COLOR.get(levelno)
        if color is None:
            return text
        return self.color(text, color | AnsiStyle.BOLD)

    def color_badge(self, text, badge):
        """
        apply the badge's hue to ``text``; custom badges get magenta


        :param text: badge label text to colorize
        :type text: str
        :param badge: badge whose hue is used, eg ``"dry"``
        :type badge: str
        :return: ``text`` with style applied if color is enabled;
                otherwise ``text`` unchanged
        :rtype: str
        """
        # local import: badges.py imports AnsiStyle from this module
        from .badges import NATIVE_BADGES

        hue = NATIVE_BADGES.get(badge, AnsiStyle.MAGENTA)
        return self.color(text, hue)

    def color_triage_tag(self, triage_tag):
        """
        apply tag-specific ANSI color to ``triage_tag``


        :param triage_tag: triage tag text,
                eg ``"BUG"``, ``"Fixme"``, ``"todo"``
        :type triage_tag: str
        :raises ValueError: ``triage_tag`` is not a recognized triage tag
        :return: ``triage_tag`` with style applied
        :rtype: str
        """
        style = self._TRIAGE_TAG2ANSI_STYLE.get(triage_tag)
        if style is None:
            raise ValueError(
                "param triage_tag {!r} is not a recognized triage tag".format(
                    triage_tag
                )
            )
        return self.color(triage_tag, style)
