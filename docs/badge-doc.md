# Badges

A **badge** is a short label that says what mode the whole run is in: a dry run, an unattended run, a forced run. Set it once, and every log line carries it, so nobody reading the output has to wonder whether anything was really changed.

kamilog only shows badges. It never makes anything dry or forced; your code does that.

## Quick Start

```python
import kamilog

log = kamilog.getLogger("copy")
log.set_badges(["dry", "yes"])
log.done("wrote a.txt")
```

```text
13:04:22 dry yes	DONE  copy: wrote a.txt
```

The badges sit between the time and the level. A tab follows them, so the level lines up across lines with different badges.

## Setting Badges

```python
log.set_badges(["dry", "chk"])           # every later line
log.done("...", badges="deploy")         # this line only, on top of the run's badges
log.done("...", badges=["dry", "yes"])   # a str or a list of str
log.done("...", inherit_badges=False)    # this line only, without the run's badges

log.clear_badges()                       # remove all run-wide badges
```

- Run-wide: `set_badges()` replaces the whole set each time; to change it, call it again with the full new list
- Clearing: `clear_badges()`, `set_badges()`, `set_badges(None)`, and `set_badges([])` all remove every run-wide badge
- Per line: `badges=` adds to the run-wide badges for that one line
- Skipping: `inherit_badges=False` leaves the run-wide badges out of one line and keeps them for the next
- Duplicates: a badge given twice prints once
- Every level method and `log()` accept `badges=` and `inherit_badges=`

## How Badges Print

- A line with no badges looks exactly as it did before badges existed
- Badges print in order of seriousness, the most serious first, whatever order you gave them: `unsafe`, `force`, and `undo` lead; `watch` and `bg` come last
- On a terminal each native badge is colored by how serious it is; in files and with `-C`, badges print as plain text
- Timestamps, if enabled, stay at the start of the line

## Native Badges

### Effect

| Badge | Color | Reads as |
| --- | --- | --- |
| `dry` | bright yellow | nothing is changed, only reported |
| `chk` | yellow | state verified, not modified |
| `mock` | yellow | the action hit a stand-in, not the real system |
| `sbx` | green | the run is isolated, so nothing outlives it |

### Safety

| Badge | Color | Reads as |
| --- | --- | --- |
| `unsafe` | bright red | verification was skipped |
| `force` | red | guards were bypassed |
| `undo` | red | a prior run is being reversed |

### Prompting

| Badge | Color | Reads as |
| --- | --- | --- |
| `yes` | yellow | prompts were auto-answered |
| `auto` | blue | no human is present |

### Error Policy

| Badge | Color | Reads as |
| --- | --- | --- |
| `strict` | green | warnings count as failures |
| `keep` | yellow | failures logged, run continues |
| `fast` | green | the first failure stops the run |
| `retries` | cyan | failed steps are attempted again |

### Execution

| Badge | Color | Reads as |
| --- | --- | --- |
| `resm` | cyan | continuing an interrupted run |
| `new` | cyan | previous state ignored, starting over |
| `offl` | cyan | no network, cached data only |
| `incr` | cyan | only what changed is processed |
| `watch` | blue | re-runs on change |
| `bg` | blue | the run is detached from the terminal |

## Custom Badges

Any other string is a custom badge, and it needs no declaration: `log.set_badges(["deploy"])` just works. Custom badges print in grey, after the native ones, in the order you gave them.

kamilog does not check names, so a misspelled native badge such as `"forse"` prints as a grey custom badge. It does not check combinations either; `dry` next to `force` is printed as given.

## With Repeated Lines

Badges work with kamilog's [diff-only output](usage_doc.md#diff-only-output): repeated lines still collapse to what changed, and the `〃` markers stay aligned under any set of badges. Multi-line messages are compared line by line, and a very long line (over 100 columns) uses spaces between markers instead of tabs.

```text
13:04:22 force dry auto	INFO  sync: sync /home/alice/docs/q3_report.pdf  ->  remote:backup  ok
13:04:22 force dry auto	INFO  sync: 〃	〃	〃	 /q4〃	〃	〃	〃	〃  ok
```

A runnable version is in [logger-badge_demo.py](../examples/logger/logger-badge_demo.py).
