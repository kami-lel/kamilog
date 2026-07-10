"""
logger-all_levels_demo.py

demonstrate all sixteen log levels with a brief description of each
"""

import sys

import kamilog
from kamilog.kamilog import AnsiRenderer, gen_comment_banner_centered

log = kamilog.getLogger(datefmt=None)
log.setLevel(kamilog.DEBUG)

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

print(gen_comment_banner_centered("standard levels", "#", renderer=renderer))
log.debug("Debugging details here")
log.info("Informational message")
log.warning("Warning message")
log.error("Error occurred")
log.critical("Critical issue")

print()
print(gen_comment_banner_centered("custom levels", "#", renderer=renderer))
log.enter("Starting database migration")
log.skip("Skipped validation step")
log.pass_("All assertions passed")
log.succ("User authentication succeeded")
log.note("Migration touches the users table")
log.tip("Run with --dry-run first to preview changes")
log.done("Migration completed successfully")
log.hint("Rerun with -v for more detail")
log.important("Back up the database before proceeding")
log.caution("This operation cannot be undone")
log.fail("Test case failed")


print()
print(
    gen_comment_banner_centered("all levels (in order)", "#", renderer=renderer)
)
log.debug("Debugging information shown only during development")
log.enter("Marks start of a routine")
log.skip("Marks skipped portion of routine")
log.succ("Subroutine or execution succeeded")
log.info("General informational message related to program function")
log.pass_("Test case passed")
log.note("General aside worth noting")
log.tip("Actionable suggestion for the user")
log.done("Entire program or major component completed successfully")
log.hint("Subtle, barely-there cue")
log.important("Emphasized information that should stand out")
log.warning("Warning condition that should be investigated")
log.caution("Risk of a negative outcome, heed carefully")
log.error("Error condition that prevented operation completion")
log.fail("Test case or subroutine/execution failed")
log.critical("Program stopping or crashing immediately")
