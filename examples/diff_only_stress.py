"""
diff_only_stress.py

high-volume demonstration of _DiffOnlyMsgFilter across diverse
message shapes and log-level functions. each section fires enough
messages for warmup (3) plus several compressed rounds.
"""

import kamilog

# server metrics — long fixed frame; only numeric readings vary  ##############
# "node=srv-01  cpu=" (17 chars) and the trailing section each compress;
# mixed info/warning levels still share the same filter window

log_srv = kamilog.getLogger("metrics")
log_srv.setLevel(kamilog.DEBUG)
log_srv.propagate = False

print("# server metrics  #" + "#" * 57)
readings = [
    (12.4,  1.9, 1.2,  "ok"),
    (14.7,  2.0, 1.1,  "ok"),
    (11.8,  1.9, 1.3,  "ok"),
    (13.2,  1.9, 1.4,  "ok"),
    (15.0,  2.0, 1.2,  "ok"),
    (16.3,  2.1, 1.0,  "ok"),
    (74.5,  2.3, 0.4,  "high"),   # spike — breaks suffix "ok" pattern
    (89.1,  2.5, 0.2,  "high"),
    (91.3,  2.6, 0.1,  "crit"),   # critical
    (14.2,  1.9, 1.2,  "ok"),     # back to normal
    (13.7,  1.8, 1.3,  "ok"),
    (12.9,  1.9, 1.1,  "ok"),     # window refills; compression resumes
]
for cpu, mem, net, st in readings:
    msg = "node=srv-01  cpu={:5.1f}%  mem={:.1f}GB  net={:.1f}Mbps  st={}".format(
        cpu, mem, net, st
    )
    if st == "crit":
        log_srv.critical(msg)
    elif st == "high":
        log_srv.warning(msg)
    else:
        log_srv.info(msg)


# api request log — fixed path; status and latency vary  ######################
# debug/succ/done/warning all go through the same window on log_api;
# the fixed prefix "GET /api/v2/users  status=" compresses first

log_api = kamilog.getLogger("api")
log_api.setLevel(kamilog.DEBUG)
log_api.propagate = False

print("\n# api requests  #" + "#" * 59)
requests = [
    (200, 12,  "alice"),
    (200, 15,  "bob"),
    (200, 11,  "carol"),
    (200, 14,  "dave"),
    (200, 13,  "eve"),
    (404,  3,  "ghost"),    # not-found — suffix changes
    (200, 16,  "frank"),
    (200, 10,  "grace"),
    (500, 42,  "system"),   # server error
    (200, 18,  "hank"),
    (200, 12,  "iris"),
    (200, 11,  "judy"),
]
for status, ms, user in requests:
    msg = "GET /api/v2/users  status={}  latency={:3d}ms  user={}".format(
        status, ms, user
    )
    if status >= 500:
        log_api.error(msg)
    elif status >= 400:
        log_api.warning(msg)
    elif ms < 12:
        log_api.succ(msg)
    else:
        log_api.info(msg)


# file scanner — enter/skip/succ/fail across a fixed base path  ###############
# "scan /opt/data/archive/2024/" (29 chars) compresses after warmup;
# enter marks start, succ/skip/fail mark outcome

log_scan = kamilog.getLogger("scanner")
log_scan.setLevel(kamilog.DEBUG)
log_scan.propagate = False

print("\n# file scanner  #" + "#" * 59)
files = [
    ("jan_export.csv",  "succ",  1024),
    ("feb_export.csv",  "succ",   980),
    ("mar_export.csv",  "succ",  1100),
    ("apr_export.csv",  "skip",     0),   # empty — skip
    ("may_export.csv",  "succ",  1050),
    ("jun_export.csv",  "fail",    -1),   # corrupt
    ("jul_export.csv",  "succ",  1020),
    ("aug_export.csv",  "succ",   995),
    ("sep_export.csv",  "succ",  1030),
    ("oct_export.csv",  "skip",     0),
    ("nov_export.csv",  "succ",  1010),
    ("dec_export.csv",  "succ",  1005),
]
for fname, outcome, rows in files:
    base = "scan /opt/data/archive/2024/{}".format(fname)
    log_scan.enter("{} starting".format(base))
    if outcome == "succ":
        log_scan.succ("{}  rows={:5d}  ok".format(base, rows))
    elif outcome == "skip":
        log_scan.skip("{}  empty — skipped".format(base))
    else:
        log_scan.fail("{}  corrupt — failed".format(base))


# test runner — enter/pass_/skip/fail with fixed test prefix  #################
# "test_auth :: case=" (19 chars) and result suffix both compress;
# mixed outcomes keep the window from stabilizing, slowing compression

log_test = kamilog.getLogger("runner")
log_test.setLevel(kamilog.DEBUG)
log_test.propagate = False

print("\n# test runner  #" + "#" * 60)
cases = [
    ("login_valid_pw",     "pass"),
    ("login_wrong_pw",     "pass"),
    ("login_empty_pw",     "pass"),
    ("login_sql_inject",   "pass"),
    ("login_unicode_pw",   "pass"),
    ("login_expired_tok",  "fail"),   # failure — suffix changes
    ("login_revoked_tok",  "fail"),
    ("login_no_session",   "pass"),
    ("login_mfa_ok",       "pass"),
    ("login_mfa_fail",     "fail"),
    ("login_rate_limit",   "skip"),   # not yet implemented
    ("login_sso_google",   "pass"),
]
for case, result in cases:
    log_test.enter("test_auth :: case={}  run".format(case))
    if result == "pass":
        log_test.pass_("test_auth :: case={}  pass".format(case))
    elif result == "fail":
        log_test.fail("test_auth :: case={}  FAIL".format(case))
    else:
        log_test.skip("test_auth :: case={}  skip".format(case))


# dual loggers — each has an independent filter window  #######################
# worker-A and worker-B share identical message structure but differ in
# "items" count; their histories never mix — compression is per-logger

log_a = kamilog.getLogger("worker-A")
log_b = kamilog.getLogger("worker-B")
for lg in (log_a, log_b):
    lg.setLevel(kamilog.DEBUG)
    lg.propagate = False

print("\n# dual loggers  #" + "#" * 59)
for i in range(1, 13):
    log_a.done("batch={:03d}  items=1000  status=complete".format(i))
    log_b.done("batch={:03d}  items=2000  status=complete".format(i))
