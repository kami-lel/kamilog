"""
Demonstrates standard levels, custom levels, and all levels with descriptions.
"""

import kamilog

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)

print("# standard levels  #" + "#" * 56)
log.debug("Debugging details here")
log.info("Informational message")
log.warning("Warning message")
log.error("Error occurred")
log.critical("Critical issue")

print("\n# custom levels  #" + "#" * 58)
log.enter("Starting database migration")
log.skip("Skipped validation step")
log.pass_("All assertions passed")
log.succ("User authentication succeeded")
log.done("Migration completed successfully")
log.fail("Test case failed")
