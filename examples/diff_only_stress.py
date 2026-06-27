"""
diff_only_stress.py

high-volume file-scanner demonstration of _DiffOnlyMsgFilter.
Two independent named loggers (scanner-2024, scanner-2025) scan
sibling archive directories; their filter windows never mix.
Long fixed paths and metadata fields produce multiple 〃\t markers
per line after the 3-message warmup completes.
"""

import kamilog

log_a = kamilog.getLogger("scanner-2024")
log_b = kamilog.getLogger("scanner-2025")
for _lg in (log_a, log_b):
    _lg.setLevel(kamilog.DEBUG)
    _lg.propagate = False

# 72-char base; first 80 chars compress to 9 markers once warmup fills
BASE_A = (
    "scan /mnt/srv/storage/datastore/archive/"
    "datasets/fiscal_2024/q1/export/"
)
BASE_B = (
    "scan /mnt/srv/storage/datastore/archive/"
    "datasets/fiscal_2025/q1/export/"
)


def log_file_scan(log, base, fname, outcome, size, crc):
    """emit enter + result for one file"""
    path = base + fname
    log.enter("{} starting".format(path))
    if outcome == "succ":
        log.succ(
            "{}  size={:7d}B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  st=ok"
            .format(path, size, crc)
        )
    elif outcome == "skip":
        log.skip(
            "{}  size=      0B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  empty"
            .format(path, crc)
        )
    else:
        log.fail(
            "{}  size={:7d}B  crc={}  "
            "owner=etl-service  mode=rw-r--r--  st=FAIL"
            .format(path, size, crc)
        )


# (fname, outcome, size_bytes, crc32)
# crc constant across ok files → long common suffix after the path
FILES_A = [
    ("batch_001.csv", "succ", 104857, "1a2b3c4d"),
    ("batch_002.csv", "succ", 104923, "1a2b3c4d"),
    ("batch_003.csv", "succ", 103982, "1a2b3c4d"),
    ("batch_004.csv", "succ", 104711, "1a2b3c4d"),
    ("batch_005.csv", "succ", 105102, "1a2b3c4d"),
    ("batch_006.csv", "skip",      0, "00000000"),
    ("batch_007.csv", "succ", 104399, "1a2b3c4d"),
    ("batch_008.csv", "succ", 104882, "1a2b3c4d"),
    ("batch_009.csv", "fail", 104771, "deadbeef"),  # bad crc
    ("batch_010.csv", "succ", 104500, "1a2b3c4d"),
    ("batch_011.csv", "succ", 104619, "1a2b3c4d"),
    ("batch_012.csv", "succ", 104930, "1a2b3c4d"),
    ("batch_013.csv", "skip",      0, "00000000"),
    ("batch_014.csv", "succ", 104733, "1a2b3c4d"),
    ("batch_015.csv", "succ", 105001, "1a2b3c4d"),
    ("batch_016.csv", "succ", 104844, "1a2b3c4d"),
    ("batch_017.csv", "succ", 104772, "1a2b3c4d"),
    ("batch_018.csv", "succ", 105033, "1a2b3c4d"),
]
FILES_B = [
    ("batch_001.csv", "succ", 209714, "2b3c4d5e"),
    ("batch_002.csv", "succ", 209846, "2b3c4d5e"),
    ("batch_003.csv", "succ", 207964, "2b3c4d5e"),
    ("batch_004.csv", "succ", 210422, "2b3c4d5e"),
    ("batch_005.csv", "fail", 208113, "cafebabe"),  # bad crc
    ("batch_006.csv", "succ", 209788, "2b3c4d5e"),
    ("batch_007.csv", "succ", 210099, "2b3c4d5e"),
    ("batch_008.csv", "skip",      0, "00000000"),
    ("batch_009.csv", "succ", 209500, "2b3c4d5e"),
    ("batch_010.csv", "succ", 209619, "2b3c4d5e"),
    ("batch_011.csv", "succ", 209930, "2b3c4d5e"),
    ("batch_012.csv", "succ", 210111, "2b3c4d5e"),
    ("batch_013.csv", "succ", 209844, "2b3c4d5e"),
    ("batch_014.csv", "skip",      0, "00000000"),
    ("batch_015.csv", "succ", 210001, "2b3c4d5e"),
    ("batch_016.csv", "succ", 209753, "2b3c4d5e"),
    ("batch_017.csv", "succ", 210288, "2b3c4d5e"),
    ("batch_018.csv", "succ", 209617, "2b3c4d5e"),
]

print("# file scanner  #" + "#" * 59)

# interleave A and B — each logger maintains its own independent window
for (fa, oa, sa, ca), (fb, ob, sb, cb) in zip(FILES_A, FILES_B):
    log_file_scan(log_a, BASE_A, fa, oa, sa, ca)
    log_file_scan(log_b, BASE_B, fb, ob, sb, cb)
