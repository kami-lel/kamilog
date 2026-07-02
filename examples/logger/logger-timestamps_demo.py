"""
logger-timestamps_demo.py

demonstrate all four ``DATEFMT_*`` timestamp formats and ``relative_to``
elapsed-time display
"""

import sys
import time

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_line_padding_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

print(gen_line_padding_centered("datefmt formats", "#", renderer=renderer))

log = kamilog.getLogger("app")
log.setLevel(kamilog.DEBUG)
log.propagate = False
log.info("no timestamp (default)")

log_t = kamilog.getLogger("app.time", datefmt=kamilog.DATEFMT_TIME)
log_t.setLevel(kamilog.DEBUG)
log_t.propagate = False
log_t.info("HH:MM:SS")

log_tms = kamilog.getLogger("app.time_ms", datefmt=kamilog.DATEFMT_TIME_MS)
log_tms.setLevel(kamilog.DEBUG)
log_tms.propagate = False
log_tms.info("HH:MM:SS.mmm")

log_dt = kamilog.getLogger("app.datetime", datefmt=kamilog.DATEFMT_DATETIME)
log_dt.setLevel(kamilog.DEBUG)
log_dt.propagate = False
log_dt.info("YYYY-MM-DD HH:MM:SS")

log_dt_ms = kamilog.getLogger(
    "app.datetime_ms", datefmt=kamilog.DATEFMT_DATETIME_MS
)
log_dt_ms.setLevel(kamilog.DEBUG)
log_dt_ms.propagate = False
log_dt_ms.info("YYYY-MM-DD HH:MM:SS.mmm")


# relative  --------------------------------------------------------------------

print()
print(gen_line_padding_centered(
    "relative_to elapsed time", "#", renderer=renderer
))

start = time.time()
log_rel = kamilog.getLogger("task", relative_to=start)
log_rel.setLevel(kamilog.DEBUG)
log_rel.propagate = False

log_rel.info("task started")
time.sleep(0.5)
log_rel.debug("0.5s elapsed")
time.sleep(1.0)
log_rel.done("1.5s elapsed — task complete")
