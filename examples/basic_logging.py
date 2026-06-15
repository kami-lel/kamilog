"""Demonstrates standard levels, custom levels, and all levels with descriptions."""

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

print("\n# all levels with descriptions  #" + "#" * 42)
log.debug("Debugging information shown only during development")
log.enter("Marks start of a routine")
log.skip("Marks skipped portion of routine")
log.info("General informational message related to program function")
log.pass_("Test case passed")
log.succ("Subroutine or execution succeeded")
log.done("Entire program or major component completed successfully")
log.warning("Warning condition that should be investigated")
log.error("Error condition that prevented operation completion")
log.fail("Test case or subroutine/execution failed")
log.critical("Program stopping or crashing immediately")
