"""
logger-timestamps-format_demo.py

demonstrate all four ``DATEFMT_*`` timestamp format constants
"""

# FIXME rewrite demos


import kamilog

print("# default: no timestamp  #" + "#" * 48)
log = kamilog.getLogger("demo")
log.setLevel(kamilog.DEBUG)
log.debug("message 1")
log.info("message 2")

print("\n# datefmt_time  #" + "#" * 55)
log = kamilog.getLogger("time", datefmt=kamilog.DATEFMT_TIME)
log.setLevel(kamilog.DEBUG)
log.debug("message 1")
log.info("message 2")

print("\n# datefmt_time_ms  #" + "#" * 52)
log = kamilog.getLogger("time_ms", datefmt=kamilog.DATEFMT_TIME_MS)
log.setLevel(kamilog.DEBUG)
log.debug("message 1")
log.info("message 2")

print("\n# datefmt_datetime  #" + "#" * 51)
log = kamilog.getLogger("datetime", datefmt=kamilog.DATEFMT_DATETIME)
log.setLevel(kamilog.DEBUG)
log.debug("message 1")
log.info("message 2")

print("\n# datefmt_datetime_ms  #" + "#" * 48)
log = kamilog.getLogger("datetime_ms", datefmt=kamilog.DATEFMT_DATETIME_MS)
log.setLevel(kamilog.DEBUG)
log.debug("message 1")
log.info("message 2")
