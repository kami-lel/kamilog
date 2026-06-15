"""Demonstrates elapsed time display with relative_to."""

import time
import kamilog

start = time.time()
log = kamilog.getLogger(relative_to=start)
log.setLevel(kamilog.DEBUG)

log.info("started")
time.sleep(0.5)
log.debug("half a second in")
time.sleep(1.0)
log.warning("one and a half seconds in")
time.sleep(2.0)
log.info("done")
