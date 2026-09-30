"""
logger-timestamps_demo.py

demonstrate the default timestamp behavior per destination, all four
``DATEFMT_*`` timestamp formats and ``relative_to`` elapsed-time display
"""

import os
import sys
import tempfile
import time

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_comment_banner_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)


# default  ---------------------------------------------------------------------

print(gen_comment_banner_centered(
    "default: console vs file", "#", renderer=renderer
))

with tempfile.TemporaryDirectory() as tmp_dir:
    log_path = os.path.join(tmp_dir, "app.log")

    # datefmt unset: console prints no timestamp, file uses DATEFMT_DATETIME_MS
    log_dft = kamilog.getLogger("app.default", filename=log_path)
    log_dft.setLevel(kamilog.DEBUG)
    log_dft.propagate = False
    log_dft.info("console: no timestamp")
    for handler in log_dft.handlers:
        handler.flush()

    print("file contents:")
    with open(log_path, encoding="utf-8") as log_file:
        print(log_file.read(), end="")
    log_dft.handlers.clear()  # release the file before the directory goes


# datefmt  ---------------------------------------------------------------------

print()
print(gen_comment_banner_centered("datefmt formats", "#", renderer=renderer))

log_t = kamilog.getLogger("app.time", datefmt=kamilog.DATEFMT_TIME)
log_t.setLevel(kamilog.DEBUG)
log_t.propagate = False
log_t.info("HH:MM:SS")

log_none = kamilog.getLogger("app.none", datefmt=None)
log_none.setLevel(kamilog.DEBUG)
log_none.propagate = False
log_none.info("no timestamp")

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
print(gen_comment_banner_centered(
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
