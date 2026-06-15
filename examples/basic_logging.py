"""Demonstrates kamilog's standard + custom log levels using the root logger."""

import kamilog

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)

# --- standard levels (same API as logging, structured output) ---
log.debug("debug detail")
log.info("informational message")
log.warning("something to watch")
log.error("an error occurred")
log.critical("critical failure")

# --- exception with traceback ---
try:
    1 / 0
except ZeroDivisionError as err:
    log.exception(err)

print()

# --- kamilog custom levels ---
log.enter("starting setup hook")
log.skip("skipping slow integration test")
log.pass_("assertion passed")
log.fail("assertion failed")
