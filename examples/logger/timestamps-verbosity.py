"""
timestamps-verbosity.py

demonstrate CLI ``-v``/``-q`` flags driving the root logger level

usage:
    python timestamps-verbosity.py          # DONE and above (default)
    python timestamps-verbosity.py -v       # INFO and above
    python timestamps-verbosity.py -vv      # DEBUG and above
    python timestamps-verbosity.py -q       # WARNING and above
    python timestamps-verbosity.py -qq      # ERROR and above
    python timestamps-verbosity.py -qqq     # CRITICAL and above
"""

from argparse import ArgumentParser
import kamilog

parser = ArgumentParser(description="verbosity demo")
kamilog.add_verbose_arguments(parser)
args = parser.parse_args()

log = kamilog.getLogger()
kamilog.set_logging_level_by_verbosity(args)

log.debug("debug detail (visible with -vv)")
log.info("info message (visible with -v)")
log.done("task completed (visible by default)")
log.warning("warning (visible with -q or less)")
log.error("error (visible with -qq or less)")
log.critical("critical (visible with -qqq or less)")
