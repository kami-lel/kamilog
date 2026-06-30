"""
logger-all_levels.py

demonstrate all eleven log levels with a brief description of each
"""

import kamilog

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)


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
