"""Demonstrates CLI verbosity flags driving the root logger level.

Usage:
    python verbosity.py          # WARNING and above
    python verbosity.py -v       # INFO and above
    python verbosity.py -vv      # DEBUG and above
    python verbosity.py -q       # suppressed
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
log.warning("warning (always visible)")
log.error("error (always visible)")
