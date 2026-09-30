"""
logger-badge_demo.py

demonstrate badges together with diff-only compression: badge
labels between the timestamp and the level, per-line compression of a
multi-line message, and space-separated dittos on a long line
"""

import sys

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_comment_banner_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

print(gen_comment_banner_centered("run-wide badges", "#", renderer=renderer))

log = kamilog.getLogger("copy")
log.setLevel(kamilog.DEBUG)
log.propagate = False

log.done("wrote a.txt")
log.set_badges(["yes", "dry"])
log.done("wrote b.txt")
log.done("wrote c.txt", badges="deploy")
log.done("wrote d.txt", inherit_badges=False)
log.clear_badges()
log.done("wrote e.txt")


print()
print(
    gen_comment_banner_centered(
        "badges keep dittos aligned", "#", renderer=renderer
    )
)

log2 = kamilog.getLogger("sync")
log2.setLevel(kamilog.DEBUG)
log2.propagate = False
log2.set_badges(["force", "dry", "auto"])

log2.info("sync /home/alice/docs/q1_report.pdf  ->  remote:backup  ok")
log2.info("sync /home/alice/docs/q2_report.pdf  ->  remote:backup  ok")
log2.info("sync /home/alice/docs/q3_report.pdf  ->  remote:backup  ok")
log2.info("sync /home/alice/docs/q4_report.pdf  ->  remote:backup  ok")
log2.info("sync /home/alice/docs/q5_report.pdf  ->  remote:backup  ok")


print()
print(gen_comment_banner_centered("multi-line message", "#", renderer=renderer))

log3 = kamilog.getLogger("build")
log3.setLevel(kamilog.DEBUG)
log3.propagate = False
log3.set_badges(["dry"])

for n in range(1, 6):
    log3.info(
        "compile /src/module_{0}.c  ok\nlink    /out/module_{0}.o  ok".format(n)
    )


print()
print(gen_comment_banner_centered("long line", "#", renderer=renderer))

log4 = kamilog.getLogger("scan")
log4.setLevel(kamilog.DEBUG)
log4.propagate = False
log4.set_badges(["chk"])

for n in range(1, 6):
    log4.info(
        "scan /var/data/archive/2026/09/shard_{0}/records.dat  "
        "checksum=ok  size=1048576  owner=backup  mode=0640  "
        "path=/mnt/nas/shard_{0}".format(n)
    )
