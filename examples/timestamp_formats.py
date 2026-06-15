"""Demonstrates timestamp format options and per-logger datefmt via named loggers."""

import kamilog

# default: time only
log = kamilog.getLogger()
log.setLevel(kamilog.INFO)
log.info("DATEFMT_TIME (default)")

# time with milliseconds — requires a second named logger to get a fresh handler
log_ms = kamilog.getLogger("ms", datefmt=kamilog.DATEFMT_TIME_MS)
log_ms.setLevel(kamilog.INFO)
log_ms.info("DATEFMT_TIME_MS")

# date + time
log_dt = kamilog.getLogger("dt", datefmt=kamilog.DATEFMT_DATETIME)
log_dt.setLevel(kamilog.INFO)
log_dt.info("DATEFMT_DATETIME")

# date + time + milliseconds
log_dt_ms = kamilog.getLogger("dt_ms", datefmt=kamilog.DATEFMT_DATETIME_MS)
log_dt_ms.setLevel(kamilog.INFO)
log_dt_ms.info("DATEFMT_DATETIME_MS")
