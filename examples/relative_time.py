"""Demonstrates elapsed time display with relative_to, including negative values."""

import time
import kamilog

# --- positive elapsed time (relative_to in the past) ---
start = time.time()
log = kamilog.getLogger("app", relative_to=start)
log.setLevel(kamilog.DEBUG)

log.info("started")             # +00:00:00.00x [INFO ] app:      started
time.sleep(0.5)
log.debug("half a second in")  # +00:00:00.5xx [DEBUG] app:      half a second in
time.sleep(1.0)
log.warning("one and a half seconds in")  # +00:00:01.5xx [WARN ] app:      one and a half seconds in

print()

# --- negative elapsed time (relative_to in the future) ---
future = time.time() + 2.0
log2 = kamilog.getLogger("countdown", relative_to=future)
log2.setLevel(kamilog.DEBUG)

log2.info("two seconds before reference")   # -00:00:02.xxx [INFO ] countdown: two seconds before reference
time.sleep(1.0)
log2.info("one second before reference")    # -00:00:01.xxx [INFO ] countdown: one second before reference
time.sleep(1.5)
log2.info("half a second after reference")  # +00:00:00.5xx [INFO ] countdown: half a second after reference
