"""
logger-diff_only_stress_demo.py

exercise _DiffOnlyMsgFilter across word-boundary, leader, and edge-case
scenarios; each demo logs 6 lines: 3 warmup, then 3 compressed
"""

# BUG refactor break behavior

import sys

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_comment_banner_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)


def run_demo(title, name, messages):
    """
    print banner, then log ``messages`` through a fresh logger
    """
    print(gen_comment_banner_centered(title, "#", renderer=renderer))
    log = kamilog.getLogger(name)
    log.setLevel(kamilog.DEBUG)
    log.propagate = False
    for msg in messages:
        log.info(msg)
    print()


# slash boundary  ##############################################################
# cut lands on "/": directory head compressed, "/file" tail printed intact
run_demo(
    "slash boundary — path prefix",
    "scan",
    [
        "scan /srv/data/archive/2024/q1/export/batch_00{}.csv ok".format(i)
        for i in range(1, 7)
    ],
)

# hyphen and underscore glue  ##################################################
# "-" and "_" are word chars: token cut falls back to the "=" before it
run_demo(
    "hyphen/underscore glue — kebab and snake tokens",
    "deploy",
    ["deploy target=prod  job=etl-run_01{}  ok".format(i) for i in range(1, 7)],
)

# equals boundary  #############################################################
# key=value pairs: cut lands on "=", key compressed, "=value" printed
run_demo(
    "equals boundary — key=value pairs",
    "sensor",
    [
        "sensor=cpu  temp=21.{}C  humid=55%  st=ok".format(i)
        for i in range(1, 7)
    ],
)

# whitespace boundary  #########################################################
# plain words: cut lands on the space before the changing field
run_demo(
    "whitespace boundary — plain words",
    "poll",
    [
        "poll queue orders worker heartbeat seq {:03d}".format(i)
        for i in range(1, 7)
    ],
)

# 2-tab fallback  ##############################################################
# unbroken hex token longer than 2 tab stops: mid-word tab-aligned cut
run_demo(
    "2-tab fallback — unbroken hash",
    "csum",
    [
        "csum sha256"
        ":9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b4a3928{:02x}".format(i)
        for i in range(1, 7)
    ],
)

# short leader  ################################################################
# run start sits < 4 columns before a tab stop: leader becomes a bare tab
# jump (leader width depends on the rendered prefix, here len("pump") works)
run_demo(
    "short leader — bare tab jump",
    "pump",
    [
        "pump pressure stable flow steady cycle {}".format(i)
        for i in range(1, 7)
    ],
)

# long leader  #################################################################
# run start sits >= 4 columns before a tab stop: leader earns its own marker
run_demo(
    "long leader — leading marker",
    "telemetry",
    [
        "telemetry uplink nominal signal clear frame {}".format(i)
        for i in range(1, 7)
    ],
)

# too short to compress  #######################################################
# common runs shorter than one marker block: lines print untouched
run_demo(
    "too short — nothing compressed",
    "up",
    [
        "up {}s node{} load {}.{}".format(i * 7, i, i, 9 - i)
        for i in range(1, 7)
    ],
)

# middle diff, common tail  ####################################################
# change sits mid-line: head and tail runs compress around it
run_demo(
    "middle diff — common head and tail",
    "copy",
    [
        "copy file_{:03d}.tmp  to /var/backup/daily  ok".format(i)
        for i in range(1, 7)
    ],
)

# identical lines  #############################################################
# whole message common: everything up to the last word compresses
run_demo(
    "identical lines — full compression",
    "heartbeat",
    ["heartbeat gateway alive"] * 6,
)
