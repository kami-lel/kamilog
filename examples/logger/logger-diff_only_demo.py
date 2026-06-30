"""
logger-diff_only_demo.py

demonstrate _DiffOnlyMsgFilter: repeated characters across the last
``window`` messages compress into 〃\\t markers; only what changed
stays visible
"""

import kamilog
from kamilog.kamilog import print_line_padding_centered

renderer = print_line_padding_centered("basic compression", "#")

log = kamilog.getLogger("sensor")
log.setLevel(kamilog.DEBUG)
log.propagate = False

log.info("sensor=cpu  load= 45.2%  temp=61C  ok")
log.info("sensor=cpu  load= 47.8%  temp=62C  ok")
log.info("sensor=cpu  load= 44.1%  temp=60C  ok")
log.info("sensor=cpu  load= 51.3%  temp=63C  ok")
log.info("sensor=cpu  load= 49.7%  temp=62C  ok")
log.info("sensor=cpu  load= 53.0%  temp=64C  ok")


print()
print_line_padding_centered(
    "pattern break and recovery", "#", renderer=renderer
)

log2 = kamilog.getLogger("sync")
log2.setLevel(kamilog.DEBUG)
log2.propagate = False

log2.info("sync /home/alice/docs/q1_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q2_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q3_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q4_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q5_report.pdf  →  remote:backup  ok")
print_line_padding_centered(
    "outlier poisons the window", "-", renderer=renderer
)
log2.warning("WARN disk 91 full on remote:backup — sync paused")
log2.info("sync /home/alice/docs/q6_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q7_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q8_report.pdf  →  remote:backup  ok")
log2.info("sync /home/alice/docs/q9_report.pdf  →  remote:backup  ok")
