"""Demonstrates timestamp format options and per-logger datefmt via named loggers."""

import kamilog

# default: no timestamp
log = kamilog.getLogger()
log.setLevel(kamilog.INFO)
log.info("(no timestamp — default)")

# time only
log_time = kamilog.getLogger("time", datefmt=kamilog.DATEFMT_TIME)
log_time.setLevel(kamilog.INFO)
log_time.info("DATEFMT_TIME")

# date + time
log_full = kamilog.getLogger("full", datefmt=kamilog.DATEFMT_DATETIME_MS)
log_full.setLevel(kamilog.INFO)
log_full.info("DATEFMT_FULL")
