"""
diff_only.py

demonstrate _DiffOnlyMsgFilter: characters repeated across the last
``window`` messages compress into 〃\\t markers; only what changed
stays visible.
"""

import kamilog

# Fixme rewrite to better demonstrate diff only function

# Diff-Only Filter Examples  ##################################################

# == periodic sensor read =====================================================
# same sensor name and unit on every line; only the reading differs.
# "sensor=cpu  load= " (18 chars) compresses to one tab; the
# temperature suffix splits at the varying digit into two short
# sub-runs (8 + 5 chars) — both stay below threshold and stay visible.

log = kamilog.getLogger("sensor")
log.setLevel(kamilog.DEBUG)
log.propagate = False

print("# sensor polling  " + "#" * 62)
print("# common prefix compresses")
log.info("sensor=cpu  load= 45.2%  temp=61C  ok")
log.info("sensor=cpu  load= 47.8%  temp=62C  ok")
log.info("sensor=cpu  load= 44.1%  temp=60C  ok")
log.info("sensor=cpu  load= 51.3%  temp=63C  ok")
log.info("sensor=cpu  load= 49.7%  temp=62C  ok")
log.info("sensor=cpu  load= 53.0%  temp=64C  ok")

# == short vs long common runs ================================================
# "step " prefix (5 chars) is below threshold — never compressed.
# ": /data/archive/2024/logs/app_2024-01-" (38 chars) compresses to
# multiple tabs; the short "err= " label (6 chars) also stays visible.

log2 = kamilog.getLogger("batch")
log2.setLevel(kamilog.DEBUG)
log2.propagate = False

print("\n# batch file processing  " + "#" * 55)
print("# 'step N' label stays (too short to compress); long path -> tabs")
log2.info("step 1: /data/archive/2024/logs/app_2024-01-10.log  err= 0")
log2.info("step 2: /data/archive/2024/logs/app_2024-01-11.log  err= 0")
log2.info("step 3: /data/archive/2024/logs/app_2024-01-12.log  err= 3")
log2.info("step 4: /data/archive/2024/logs/app_2024-01-13.log  err= 0")
log2.info("step 5: /data/archive/2024/logs/app_2024-01-14.log  err= 0")
log2.info("step 6: /data/archive/2024/logs/app_2024-01-15.log  err= 7")

# == pattern break and recovery ===============================================
# a structurally different message poisons all three window slots.
# common ground with the regular lines shrinks so less compresses.
# once the window refills with regular lines, full compression returns.

log3 = kamilog.getLogger("sync")
log3.setLevel(kamilog.DEBUG)
log3.propagate = False

print("\n# sync log — pattern break and recovery  " + "#" * 39)
print("# warmup")
log3.info("sync /home/alice/docs/q1_report.pdf  →  remote:backup  ok")
log3.info("sync /home/alice/docs/q2_report.pdf  →  remote:backup  ok")
log3.info("sync /home/alice/docs/q3_report.pdf  →  remote:backup  ok")
print("# steady: prefix and suffix compress")
log3.info("sync /home/alice/docs/q4_report.pdf  →  remote:backup  ok")
log3.info("sync /home/alice/docs/q5_report.pdf  →  remote:backup  ok")
print("# one different message poisons the window")
log3.info("WARN disk 91% full on remote:backup — sync paused")
print("# recovery: outlier in window — sync lines print in full")
log3.info("sync /home/alice/docs/q6_report.pdf  →  remote:backup  ok")
log3.info("sync /home/alice/docs/q7_report.pdf  →  remote:backup  ok")
log3.info("sync /home/alice/docs/q8_report.pdf  →  remote:backup  ok")
print("# full recovery: outlier aged out of window")
log3.info("sync /home/alice/docs/q9_report.pdf  →  remote:backup  ok")

# == multi-logger: different timestamp settings ================================
# three independent loggers emit the same pipeline messages; each uses
# a different timestamp format — none, time-only, and time+ms — so
# their rendered prefix widths differ.  each logger's
# _DiffOnlyMsgFilter was constructed with a matching formatter so
# count_prefix_chars returns the correct width; 〃\t lands on an
# 8-column tab stop from each line's own start regardless of how wide
# the prefix is.

log_none = kamilog.getLogger("node")
log_none.setLevel(kamilog.DEBUG)
log_none.propagate = False

log_t = kamilog.getLogger("node.t", datefmt=kamilog.DATEFMT_TIME)
log_t.setLevel(kamilog.DEBUG)
log_t.propagate = False

log_ms = kamilog.getLogger("node.ms", datefmt=kamilog.DATEFMT_TIME_MS)
log_ms.setLevel(kamilog.DEBUG)
log_ms.propagate = False

msgs = [
    "job=compress  src=archive/2025-01  out=store/q1  rows=14332",
    "job=compress  src=archive/2025-02  out=store/q1  rows=14019",
    "job=compress  src=archive/2025-03  out=store/q1  rows=15204",
    "job=compress  src=archive/2025-04  out=store/q1  rows=13887",
    "job=compress  src=archive/2025-05  out=store/q1  rows=14556",
    "job=compress  src=archive/2025-06  out=store/q1  rows=14103",
]

print("\n# multi-logger: different timestamp settings  " + "#" * 34)
print("# warmup — each logger builds its own window independently")
for msg in msgs[:3]:
    log_none.info(msg)
    log_t.info(msg)
    log_ms.info(msg)
print("# compression: marker column shifts per logger but stays on tab stop")
for msg in msgs[3:]:
    log_none.info(msg)
    log_t.info(msg)
    log_ms.info(msg)
