"""
Demonstrates diff-only message filtering: characters unchanged across
the last 3 messages are blanked out, highlighting only what changed.
"""

import kamilog

log = kamilog.getLogger()
log.setLevel(kamilog.DEBUG)

print(
    "# first 3 messages shown in full (warmup)  #"
    + "#" * 35
)
log.info("epoch 01 | loss: 0.8231 | acc: 61.2% | lr: 0.0100")
log.info("epoch 02 | loss: 0.7654 | acc: 63.8% | lr: 0.0100")
log.info("epoch 03 | loss: 0.7102 | acc: 65.4% | lr: 0.0100")

print(
    "\n# subsequent messages show only what changed  #"
    + "#" * 31
)
log.info("epoch 04 | loss: 0.6587 | acc: 67.1% | lr: 0.0100")
log.info("epoch 05 | loss: 0.6103 | acc: 68.9% | lr: 0.0095")
log.info("epoch 06 | loss: 0.5741 | acc: 70.3% | lr: 0.0095")
log.info("epoch 07 | loss: 0.5318 | acc: 72.0% | lr: 0.0090")
