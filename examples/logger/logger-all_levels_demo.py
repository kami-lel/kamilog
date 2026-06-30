"""
logger-all_levels_demo.py

demonstrate all eleven log levels with a brief description of each
"""

import kamilog
from kamilog.kamilog import print_line_padding_centered

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)


renderer = print_line_padding_centered("standard levels", "#")
log.debug("Debugging details here")
log.info("Informational message")
log.warning("Warning message")
log.error("Error occurred")
log.critical("Critical issue")

print()
print_line_padding_centered("custom levels", "#", renderer=renderer)
log.enter("Starting database migration")
log.skip("Skipped validation step")
log.pass_("All assertions passed")
log.succ("User authentication succeeded")
log.done("Migration completed successfully")
log.fail("Test case failed")


print()
print_line_padding_centered("all levels (in order)", "#", renderer=renderer)
log.debug("Debugging information shown only during development")
log.enter("Marks start of a routine")
log.skip("Marks skipped portion of routine")
log.succ("Subroutine or execution succeeded")
log.info("General informational message related to program function")
log.pass_("Test case passed")
log.done("Entire program or major component completed successfully")
log.warning("Warning condition that should be investigated")
log.error("Error condition that prevented operation completion")
log.fail("Test case or subroutine/execution failed")
log.critical("Program stopping or crashing immediately")
