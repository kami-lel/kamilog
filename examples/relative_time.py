"""Demonstrates elapsed time display with relative_to, including negative values."""

import time
import kamilog

# --- positive elapsed time (relative_to in the past) ---
start = time.time()
log = kamilog.getLogger(relative_to=start)
log.setLevel(kamilog.DEBUG)

log.info("started")             # +00:00:00.00x
time.sleep(0.5)
log.debug("half a second in")  # +00:00:00.5xx
time.sleep(1.0)
log.warning("one and a half seconds in")  # +00:00:01.5xx

print()

# --- negative elapsed time (relative_to in the future) ---
future = time.time() + 2.0
log2 = kamilog.getLogger("countdown", relative_to=future)
log2.setLevel(kamilog.DEBUG)
log2.propagate = False

log2.info("two seconds before reference")   # -00:00:02.xxx
time.sleep(1.0)
log2.info("one second before reference")    # -00:00:01.xxx
time.sleep(1.5)
log2.info("half a second after reference")  # +00:00:00.5xx
