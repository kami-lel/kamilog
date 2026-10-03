"""
logger-badge-all_demo.py

demonstrate every native badge plus a custom one, one per log entry,
grouped by the category table in docs/badge-doc.md
"""

import sys

import kamilog
from kamilog import AnsiRenderer, gen_comment_banner_centered

log = kamilog.getLogger(datefmt=None)
log.setLevel(kamilog.DEBUG)
log.propagate = False

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

print(gen_comment_banner_centered("mode", "#", renderer=renderer))
log.info("reporting only, nothing modified", badges="dry")
log.info("validating input, nothing modified", badges="chk")
log.info("hitting stand-in payment gateway", badges="mock")
log.info("running isolated, nothing outlives it", badges="sandbox")

print()
print(gen_comment_banner_centered("guard", "#", renderer=renderer))
log.info("bypassing the lock file check", badges="force")
log.info("reverting the previous migration", badges="undo")
log.info("granting write access to the shared bucket", badges="grant")
log.info("running with superuser rights", badges="elevated")
log.info("calling the deprecated v1 endpoint", badges="legacy")
log.info("using the experimental scheduler", badges="unstable")

print()
print(gen_comment_banner_centered("data", "#", renderer=renderer))
log.info("creating output/report.csv", badges="new")
log.info("overwriting output/report.csv", badges="owr")
log.info("deleting output/report.csv", badges="del")
log.info("renaming draft.csv to report.csv", badges="mv")
log.info("duplicating report.csv to report.bak", badges="cp")
log.info("serving report.csv from cache", badges="cached")
log.info("serving report.csv older than expected", badges="stale")

print()
print(gen_comment_banner_centered("automation", "#", renderer=renderer))
log.info("unattended run, auto-answering prompts", badges="auto")
log.info("ignoring previous state, starting over", badges="fresh")
log.info("continuing the interrupted run", badges="resume")
log.info("running without network, cached data only", badges="offline")

print()
print(gen_comment_banner_centered("process", "#", renderer=renderer))
log.info("re-running on file change", badges="watch")
log.info("running detached from the terminal", badges="bg")

print()
print(gen_comment_banner_centered("recovery", "#", renderer=renderer))
log.info("repeating the failed upload", badges="retry")
log.info("taking the secondary path after primary failed", badges="fallback")
log.info("skipping the broken validation step", badges="skip")
log.info("hitting the 30 second time limit", badges="timeout")
log.info("cutting the run short on purpose", badges="abort")

print()
print(gen_comment_banner_centered("custom", "#", renderer=renderer))
log.info("pushing to the eu-west region", badges="eu-west")
