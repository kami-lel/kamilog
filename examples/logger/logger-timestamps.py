"""
logger-timestamps.py

demonstrate named loggers with various ``datefmt`` and timestamp options
"""

import kamilog

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)
log.info("info message")
log.warning("warning message")

log_a = kamilog.getLogger("a")
log_a.setLevel(kamilog.DEBUG)
log_a.propagate = False
log_a.debug("first message")
log_a.error("second message")

log_db = kamilog.getLogger("database")
log_db.setLevel(kamilog.DEBUG)
log_db.propagate = False
log_db.warning("first message")
log_db.info("second message")

log_time = kamilog.getLogger("srv", datefmt=kamilog.DATEFMT_TIME)
log_time.setLevel(kamilog.DEBUG)
log_time.propagate = False
log_time.debug("first message")
log_time.info("second message")

log_full = kamilog.getLogger("worker_pool", datefmt=kamilog.DATEFMT_DATETIME)
log_full.setLevel(kamilog.DEBUG)
log_full.propagate = False
log_full.error("first message")
log_full.critical("second message")

log_ms = kamilog.getLogger("api", datefmt=kamilog.DATEFMT_TIME_MS)
log_ms.setLevel(kamilog.DEBUG)
log_ms.propagate = False
log_ms.warning("first message")
log_ms.debug("second message")

log_full_ms = kamilog.getLogger("hooks_runner", datefmt=kamilog.DATEFMT_DATETIME_MS)
log_full_ms.setLevel(kamilog.DEBUG)
log_full_ms.propagate = False
log_full_ms.enter("entering hook")
log_full_ms.pass_("hook passed")
