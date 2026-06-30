"""
logger-timestamps-relative_demo.py

demonstrate elapsed time display via ``relative_to``, including negative values
"""

import time
import kamilog

print("# positive elapsed time (relative_to in the past)  #" + "#" * 30)
start = time.time()
log = kamilog.getLogger("app", relative_to=start)
log.setLevel(kamilog.DEBUG)
log.propagate = False

log.info("started")
time.sleep(0.5)
log.debug("half a second elapsed")
time.sleep(1.0)
log.warning("one and a half seconds elapsed")

print("\n# negative elapsed time (relative_to in the future)  #" + "#" * 28)
future = time.time() + 2.0
log2 = kamilog.getLogger("countdown", relative_to=future)
log2.setLevel(kamilog.DEBUG)
log2.propagate = False

log2.info("two seconds before reference")
time.sleep(1.0)
log2.info("one second before reference")
time.sleep(1.5)
log2.info("half a second after reference")
