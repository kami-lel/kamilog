"""
logger-diff_only_stress_demo.py

contrast short and long message compression under _DiffOnlyMsgFilter
"""

import sys

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_comment_banner_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

print(gen_comment_banner_centered("short messages", "#", renderer=renderer))

log_short = kamilog.getLogger("sensor")
log_short.setLevel(kamilog.DEBUG)
log_short.propagate = False

readings = [
    (21.4, 55, "ok"),
    (21.6, 55, "ok"),
    (21.9, 55, "ok"),
    (22.1, 55, "ok"),
    (22.3, 55, "ok"),
    (22.0, 56, "ok"),
    (74.5, 92, "high"),
    (89.1, 96, "crit"),
    (21.2, 54, "ok"),
    (21.1, 55, "ok"),
]

for temp, humid, status in readings:
    msg = "sensor=cpu  temp={:5.1f}C  humid={:3d}%  st={}".format(
        temp, humid, status
    )
    if status == "crit":
        log_short.critical(msg)
    elif status == "high":
        log_short.warning(msg)
    else:
        log_short.info(msg)


print()
print(gen_comment_banner_centered("long messages", "#", renderer=renderer))

log_long = kamilog.getLogger("scanner")
log_long.setLevel(kamilog.DEBUG)
log_long.propagate = False

BASE = (
    "scan /mnt/srv/storage/datastore/archive/datasets/fiscal_2024/q1/export/"
)

FILES = [
    ("batch_001.csv", "succ", 104857, "1a2b3c4d"),
    ("batch_002.csv", "succ", 104923, "1a2b3c4d"),
    ("batch_003.csv", "succ", 103982, "1a2b3c4d"),
    ("batch_004.csv", "succ", 104711, "1a2b3c4d"),
    ("batch_005.csv", "succ", 105102, "1a2b3c4d"),
    ("batch_006.csv", "skip", 0,      "00000000"),
    ("batch_007.csv", "succ", 104399, "1a2b3c4d"),
    ("batch_008.csv", "succ", 104882, "1a2b3c4d"),
    ("batch_009.csv", "fail", 104771, "deadbeef"),
    ("batch_010.csv", "succ", 104500, "1a2b3c4d"),
]

for fname, outcome, size, crc in FILES:
    path = BASE + fname
    log_long.enter("{} starting".format(path))
    if outcome == "succ":
        log_long.succ(
            "{}  size={:7d}B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  st=ok".format(
                path, size, crc
            )
        )
    elif outcome == "skip":
        log_long.skip(
            "{}  size=      0B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  empty".format(path, crc)
        )
    else:
        log_long.fail(
            "{}  size={:7d}B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  st=FAIL".format(
                path, size, crc
            )
        )
