# Badges Documentation

A **badge** is a short label that says what mode the whole run is in: a dry run, an unattended run, a forced run. Set it once, and every log line carries it, so nobody reading the output has to wonder whether anything was really changed.

kamilog only shows badges. It never makes anything dry or forced; your code does that.













## Usage

```python
import kamilog

log = kamilog.getLogger("copy")
log.setLevel(kamilog.DEBUG)

log.set_badges(["dry", "yes"])  # every later line, replaces any earlier set
log.done("wrote a.txt")
log.done("wrote b.txt", badges="deploy")  # this line only, on top of the set
log.done("wrote c.txt", is_inheriting_badges=False)  # this line only, without the set

log.clear_badges()  # same as set_badges(), (None) or ([])
log.done("wrote d.txt")
```

```text
dry yes	DONE  copy: wrote a.txt
dry yes deploy	DONE  copy: wrote b.txt
DONE  copy: wrote c.txt
DONE  copy: wrote d.txt
```

`badges` takes a string or a list, and every level method and `log()` accept it along with `is_inheriting_badges`. On a terminal each native badge is colored by how serious it is; files and `-C` output stay plain.

Badges print most serious first, whatever order you give them: `unsafe`, `force`, and `undo` lead, and `watch` and `bg` come last.













## Native Badges

Effect:

| Badge | CLI Analogue | Color | Remark |
| --- | --- | --- | --- |
| `dry` | `--dry-run`, `rsync -n` | `BRIGHT_YELLOW` | nothing is changed, only reported |
| `chk` | `ansible --check`, `black --check` | `YELLOW` | short for *check*; state verified, not modified |
| `mock` | stubbed or fake backend | `YELLOW` | the action hit a stand-in, not the real system |
| `sbx` | `docker run --rm`, throwaway environment | `GREEN` | short for *sandbox*; the run is isolated, so nothing outlives it |

Safety:

| Badge | CLI Analogue | Color | Remark |
| --- | --- | --- | --- |
| `unsafe` | `git --no-verify`, `curl -k` | `BRIGHT_RED` | verification was skipped |
| `force` | `-f`, `git push --force` | `RED` | guards were bypassed |
| `undo` | `--rollback` | `RED` | a prior run is being reversed |

Prompting:

| Badge | CLI Analogue | Color | Remark |
| --- | --- | --- | --- |
| `yes` | `-y`, `apt -y` | `YELLOW` | prompts were auto-answered |
| `auto` | `--non-interactive`, CI, cron | `BLUE` | short for *automatic*; no human is present |

Error Policy:

| Badge | CLI Analogue | Color | Remark |
| --- | --- | --- | --- |
| `strict` | `--strict`, `-Werror` | `GREEN` | warnings count as failures |
| `keep` | `make -k`, `--continue-on-error` | `YELLOW` | failures logged, run continues |
| `fast` | `pytest -x`, `set -e` | `GREEN` | the first failure stops the run |
| `retries` | `curl --retry`, `--retries N` | `CYAN` | failed steps are attempted again |

Execution:

| Badge | CLI Analogue | Color | Remark |
| --- | --- | --- | --- |
| `resm` | `wget -c`, `rsync --partial` | `CYAN` | short for *resume*; continuing an interrupted run |
| `new` | `--no-cache`, `--fresh` | `CYAN` | previous state ignored, starting over |
| `offl` | `pip --no-index`, `npm --offline` | `CYAN` | short for *offline*; no network, cached data only |
| `incr` | `rsync`, only changed items | `CYAN` | short for *incremental*; only what changed is processed |
| `watch` | `--watch` | `BLUE` | re-runs on change |
| `bg` | `docker -d`, `&` | `BLUE` | short for *background*; the run is detached from the terminal |













## Custom Badges

Any other string works as a badge, with no declaration, and prints grey after the native ones. Names are not checked, so a misspelled native badge such as `"forse"` prints as a grey custom one.
