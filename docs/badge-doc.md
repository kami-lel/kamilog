# Badges Documentation

A **badge** is a decorative tag flagging a log entry as worth attention.

A badge may mark one entry, or be set once to carry across every later line. kamilog only shows badges; your code decides what's dry or forced. Badges are a feature of the [logger](log-doc.md), and [deeds](deed-doc.md) accept them per line.













## Usage

```python
import kamilog

log = kamilog.getLogger("copy")
log.setLevel(kamilog.DEBUG)

log.set_persistent_badges(["dry", "yes"])  # every later line, replaces any earlier set
log.done("wrote a.txt")
log.done("wrote b.txt", badges="deploy")  # this line only, on top of the set
log.done("wrote c.txt", is_inheriting_badges=False)  # this line only, without the set

log.clear_persistent_badges()    # or equivalently
log.set_persistent_badges(None)  # or equivalently
log.set_persistent_badges([])
log.done("wrote d.txt")
```

```text
DONE  dry yes	copy: wrote a.txt
DONE  dry yes deploy	copy: wrote b.txt
DONE  copy: wrote c.txt
DONE  copy: wrote d.txt
```

`badges` takes a string or a list, and every level method and `log()` accept it along with `is_inheriting_badges`. On a terminal each native badge is colored by how serious it is; files and `-C` output stay plain.

Badges print most serious first, whatever order you give them: `force` and `undo` lead, and `watch` and `bg` come last.













## Native Badges

Mode:

| Badge | Color | Remark |
| --- | --- | --- |
| `dry` | | runs in dry mode, only report |
| `chk` | | runs *check* and validation, nothing modified |
| `mock` | | hits stand-in, not real system |
| `sandbox` | | runs isolated, nothing outlives it |

Guard:

| Badge | Color | Remark |
| --- | --- | --- |
| `force` | | bypasses guard or verification |
| `undo` | | reverses prior run |
| `grant` | | grants or widens access right |
| `elevated` | | runs w/ superuser or admin rights |
| `legacy` | | uses deprecated or outdated feature/API |
| `unstable` | | uses unstable or experimental feature/interface |

Data:

| Badge | Color | Remark |
| --- | --- | --- |
| `new` | | creates file or directory |
| `owr` | | *overwrites* existing value or file |
| `del` | | *deletes* something |
| `mv` | | *moves* or renames file or record |
| `cp` | | *duplicates* file or record |
| `cached` | | result from cache, not recomputed |
| `stale` | | uses data or state older than expected |

Automation:

| Badge | Color | Remark |
| --- | --- | --- |
| `auto` | | unattended, auto-answers prompts |
| `fresh` | | ignores previous state, starts over |
| `resume` | | continues interrupted run |
| `offline` | | runs w/o network, cached data only |

Process:

| Badge | Color | Remark |
| --- | --- | --- |
| `watch` | | re-runs on change |
| `bg` | | runs detached from terminal, *background* |

Recovery:

| Badge | Color | Remark |
| --- | --- | --- |
| `retry` | | repeat attempt |
| `fallback` | | takes secondary path after primary fails |
| `skip` | | skips step, or tolerates failure |
| `timeout` | | hits time limit |
| `abort` | | cuts short on purpose |













## Custom Badges

Any other string works as a badge, with no declaration, and prints magenta after the native ones. Names are not checked, so a misspelled native badge such as `"forse"` prints as a magenta custom one.

A nightly sync job run by cron, pushing to the `eu-west` region, mixes native and custom badges:

```python
import kamilog

log = kamilog.getLogger("sync")
log.setLevel(kamilog.DEBUG)

log.set_persistent_badges(["eu-west", "auto", "keep"])
log.done("synced 120 files")
```

```
DONE  auto keep eu-west	sync: synced 120 files
```

`auto` and `keep` are native and lead, colored by severity, while `eu-west` is custom and follows in magenta.
