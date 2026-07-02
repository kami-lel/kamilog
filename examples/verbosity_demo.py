"""
verbosity_demo.py

demonstrate CLI ``-v``/``-q`` flags driving the root logger level via
custom log levels and stdlib levels

usage:
    python verbosity_demo.py          # DONE and above (default)
    python verbosity_demo.py -v       # INFO and above
    python verbosity_demo.py -vv      # ENTER, SKIP, SUCC and above
    python verbosity_demo.py -vvv     # DEBUG and above
    python verbosity_demo.py -q       # WARNING and above
    python verbosity_demo.py -qq      # ERROR and above
    python verbosity_demo.py -qqq     # CRITICAL and above
"""

from argparse import ArgumentParser
import kamilog

parser = ArgumentParser(description="verbosity demo")
kamilog.add_verbose_arguments(parser)
args = parser.parse_args()

log = kamilog.getLogger()
kamilog.set_logging_level_by_verbosity(args)

log.debug("debug detail (visible with -vvv)")
log.enter("entering subroutine (visible with -vv)")
log.skip("skipped step (visible with -vv)")
log.succ("operation succeeded (visible with -vv)")
log.info("info message (visible with -v)")
log.pass_("test passed (visible with -v)")
log.done("task completed (visible by default)")
log.warning("warning (visible with -q or less)")
log.error("error (visible with -qq or less)")
log.fail("test failed (visible with -qq or less)")
log.critical("critical (visible with -qqq or less)")
