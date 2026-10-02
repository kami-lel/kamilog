"""
custom log levels: the ``_CustomLogLevel`` enum and the public level constants
"""

import logging
from enum import IntEnum

class _CustomLogLevel(IntEnum):
    """
    custom log level IntEnum with padded 5-char display name


    :param value: numeric log level (used as the enum's int value)
    :type value: int
    :param display: padded 5-character display string for formatter output
    :type display: str
    """

    def __new__(cls, value, display):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.display = display
        return obj

    ENTER = (15, "ENTER")
    SKIP = (16, "SKIP ")
    SUCC = (17, "SUCC.")
    PASS = (21, "PASS ")
    NOTE = (23, "NOTE ")
    TIP = (24, "TIP  ")
    DONE = (25, "DONE ")
    HINT = (26, "HINT ")
    IMPORTANT = (27, "IMPT.")
    CAUTION = (31, "CAUT.")
    FAIL = (45, "FAIL ")


# level registration during import
for _lvl in _CustomLogLevel:
    logging.addLevelName(int(_lvl), _lvl.name)


# constants  ===================================================================

NOTSET = logging.NOTSET  # 0
DEBUG = logging.DEBUG  # 10
ENTER = _CustomLogLevel.ENTER  # 15
SKIP = _CustomLogLevel.SKIP  # 16
SUCC = _CustomLogLevel.SUCC  # 17
INFO = logging.INFO  # 20
PASS = _CustomLogLevel.PASS  # 21
NOTE = _CustomLogLevel.NOTE  # 23
TIP = _CustomLogLevel.TIP  # 24
DONE = _CustomLogLevel.DONE  # 25
HINT = _CustomLogLevel.HINT  # 26
IMPORTANT = _CustomLogLevel.IMPORTANT  # 27
WARNING = logging.WARNING  # 30
CAUTION = _CustomLogLevel.CAUTION  # 31
ERROR = logging.ERROR  # 40
FAIL = _CustomLogLevel.FAIL  # 45
CRITICAL = logging.CRITICAL  # 50
