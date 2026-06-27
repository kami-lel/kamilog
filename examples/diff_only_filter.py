"""
Demonstrates diff-only message filtering: characters unchanged across
the last 3 messages are blanked, highlighting only what changed.

Only contiguous runs of 8+ common characters are replaced — spaces
within a run count toward its length but are not replaced themselves.
"""

import kamilog

# ── training progress ─────────────────────────────────────────────────────────
# "epoch 0" (7 chars) is one below the 8-char threshold, so it stays
# visible. " | loss: 0." (11 chars) and " | acc: 6" (9 chars) exceed
# it and get blanked. The lr suffix also blanks until the rate changes.

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)

print("# training log — first 3 shown in full (warmup)  #" + "#" * 29)
log.info("epoch 01 | loss: 0.8231 | acc: 61.2% | lr: 0.0100")
log.info("epoch 02 | loss: 0.7654 | acc: 63.8% | lr: 0.0100")
log.info("epoch 03 | loss: 0.7102 | acc: 65.4% | lr: 0.0100")

print("\n# only changing values remain  #" + "#" * 47)
log.info("epoch 04 | loss: 0.6587 | acc: 67.1% | lr: 0.0100")
log.info("epoch 05 | loss: 0.6103 | acc: 68.9% | lr: 0.0095")
log.info("epoch 06 | loss: 0.5741 | acc: 70.3% | lr: 0.0095")
log.info("epoch 07 | loss: 0.5318 | acc: 72.0% | lr: 0.0090")

# ── job log: short prefix vs long suffix ──────────────────────────────────────
# "job N" stays because the common "job " prefix is only 4 chars (<8).
# ": completed in " (15 chars) and "s  (200 OK)" (11 chars) are blanked.
# When job 6 fails, the long common suffix changes — less gets blanked
# until a new steady pattern is re-established.

log2 = kamilog.getLogger("jobs")
log2.setLevel(kamilog.DEBUG)
log2.propagate = False

print("\n# job log — short 'job N' prefix stays visible  #" + "#" * 31)
log2.info("job 1: completed in 2.3s  (200 OK)")
log2.info("job 2: completed in 4.1s  (200 OK)")
log2.info("job 3: completed in 1.7s  (200 OK)")

print("\n# common boilerplate blanked, only timing changes  #" + "#" * 28)
log2.info("job 4: completed in 3.0s  (200 OK)")
log2.info("job 5: completed in 0.9s  (200 OK)")
log2.info("job 6: failed     in 5.2s  (500 ERR)")  # breaks pattern
log2.info("job 7: completed in 2.1s  (200 OK)")

# ── pattern break and recovery ────────────────────────────────────────────────
# A one-off different message poisons the 3-message window, reducing
# how much can be blanked. Blanking gradually recovers as the steady
# pattern returns.

log3 = kamilog.getLogger("http")
log3.setLevel(kamilog.DEBUG)
log3.propagate = False

print("\n# http log — pattern break then recovery  #" + "#" * 37)
log3.info("GET /api/v1/users/42/profile     200")
log3.info("GET /api/v1/users/42/settings    200")
log3.info("GET /api/v1/users/42/activity    200")
log3.info("GET /api/v1/users/42/followers   200")
log3.info("POST /api/v1/users/42/follow     201")  # interrupts pattern
log3.info("GET /api/v1/users/42/following   200")
log3.info("GET /api/v1/users/42/profile     200")
log3.info("GET /api/v1/users/42/settings    200")
