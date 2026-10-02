"""
logger-deed_demo.py

demonstrate deed log methods: plain form, track form on success and on
failure, late arguments, failure as a value, and `suppress`
"""

import sys

import kamilog
from kamilog import AnsiRenderer, gen_comment_banner_centered

# repeated calls share one renderer instead of re-detecting TTY state
renderer = AnsiRenderer(sys.stdout)

log = kamilog.getLogger("deed")
log.setLevel(kamilog.DEBUG)
log.propagate = False


def _banner(title):
    print()
    print(gen_comment_banner_centered(title, "#", renderer=renderer))


print(gen_comment_banner_centered("plain form", "#", renderer=renderer))

log.create_file("out/a.txt")
log.cp_file("a.txt", "backup/a.txt")
log.append_file("out/a.txt")
log.chmod_file("run.sh", "755")
log.download("https://example.com/a.zip")
log.rm_file("tmp/a.txt")
log.rm_file("tmp/b.txt", level=kamilog.INFO)
log.skip_file("keep/a.txt")
log.cp_file("a.txt", "backup/a.txt", badges="dry")


_banner("track form: success")

with log.track.cp_file("a.txt", "backup/a.txt"):
    pass

with log.track.run_command("make", level=kamilog.DEBUG):
    pass


_banner("track form: failure")

try:
    with log.track.cp_file("a.txt", "/root/a.txt"):
        raise PermissionError(13, "Permission denied", "/root/a.txt")
except PermissionError:
    print("the exception still propagated")

with log.track.rm_file("tmp/c.txt", suppress=True):
    raise OSError("device busy")
print("suppress carried on")

with log.track.rm_file(
    "tmp/d.txt", suppress=True, err_level=kamilog.INFO
):
    raise OSError("already gone")


_banner("track form: handle")

with log.track.download("https://example.com/b.zip") as act:
    act.set(destination="b.zip")

with log.track.download("https://example.com/c.zip") as act:
    pass

with log.track.run_command("make") as act:
    act.fail("exit 2")

with log.track.download("https://example.com/d.zip") as act:
    act.fail("status 404")
