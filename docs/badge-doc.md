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
| `dry` | `BRIGHT_YELLOW` | runs in dry mode, only report |
| `chk` | `YELLOW` | runs *check* and validation, nothing modified |
| `mock` | `YELLOW` | hits stand-in, not real system |
| `sandbox` | `GREEN` | runs isolated, nothing outlives it |

Guard:

| Badge | Color | Remark |
| --- | --- | --- |
| `force` | `RED` | bypasses guard or verification |
| `undo` | `RED` | reverses prior run |
| `grant` | `YELLOW` | grants or widens access right |
| `elevated` | `BRIGHT_RED` | runs w/ superuser or admin rights |
| `legacy` | `YELLOW` | uses deprecated or outdated feature/API |
| `unstable` | `BRIGHT_YELLOW` | uses unstable or experimental feature/interface |

Data:

| Badge | Color | Remark |
| --- | --- | --- |
| `new` | `GREEN` | creates file or directory |
| `owr` | `YELLOW` | *overwrites* existing value or file |
| `del` | `RED` | *deletes* something |
| `mv` | `CYAN` | *moves* or renames file or record |
| `cp` | `CYAN` | *duplicates* file or record |
| `cached` | `CYAN` | result from cache, not recomputed |
| `stale` | `YELLOW` | uses data or state older than expected |

Automation:

| Badge | Color | Remark |
| --- | --- | --- |
| `auto` | `BLUE` | unattended, auto-answers prompts |
| `fresh` | `CYAN` | ignores previous state, starts over |
| `resume` | `CYAN` | continues interrupted run |
| `offline` | `CYAN` | runs w/o network, cached data only |

Process:

| Badge | Color | Remark |
| --- | --- | --- |
| `watch` | `BLUE` | re-runs on change |
| `bg` | `BLUE` | runs detached from terminal, *background* |

Recovery:

| Badge | Color | Remark |
| --- | --- | --- |
| `retry` | `CYAN` | repeat attempt |
| `fallback` | `YELLOW` | takes secondary path after primary fails |
| `timeout` | `RED` | hits time limit |
| `abort` | `BRIGHT_RED` | cuts short on purpose |













## Custom Badges

Any other string works as a badge, with no declaration, and prints magenta after the native ones. Names are not checked, so a misspelled native badge such as `"forse"` prints as a magenta custom one.

A nightly sync job run by cron, pushing to the `eu-west` region, mixes native and custom badges:

```python
import kamilog

log = kamilog.getLogger("sync")
log.setLevel(kamilog.DEBUG)

log.set_persistent_badges(["eu-west", "auto", "retry"])
log.done("synced 120 files")
```

```
DONE  retry auto eu-west	sync: synced 120 files
```

`retry` and `auto` are native and lead, colored by severity, while `eu-west` is custom and follows in magenta.
