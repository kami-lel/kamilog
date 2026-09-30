# Operation Badges

*Status: implemented*

An **operation badge** labels the mode the whole run is in, such as a dry run or an unattended run. Badges combine, and they are usually set once for a run. kamilog only records and displays them; it never makes an operation dry or forced, since the caller's code does that.

Two terms are used throughout:

- Badge: a label string; the native ones below carry a defined meaning and hue, and any other string is a custom badge
- Label: the bare lowercase word a badge prints

## Display

- Position: after the level, before the source label. The badge segment sits between two tabs, `level<tab>badges<tab>source`. The timestamp, when enabled, keeps its place at the line start and the level follows it as usual.
- No badges: a line with no badges prints exactly as it always did, with no added tabs.
- Form: bare lowercase labels separated by single spaces, with no brackets or other delimiter.
- Order: badge labels sorted by descending priority, the highest first (see [Native Badges](#native-badges)), whatever order the caller gave; ties keep the order given.
- Width: tab stops are 8 columns. The badges start on the first tab stop after the level, and the source and message on the first tab stop strictly after the badges, so a badge run ending exactly on a stop pushes the source a full stop further. Lines whose badges end within the same stop share a message column.
- Plain output: files and `-C` output keep the bare labels and real tab characters.
- Color: a foreground hue per native label on a TTY, chosen by severity (see [Native Badges](#native-badges)); any other label is grey, the default for a custom badge. The separating spaces and tabs are never colored.
- Uniqueness: no label is used twice across badges, so a label is unambiguous on sight.

```text
13:04:22 DONE  copy: wrote a.txt
13:04:22 DONE 	dry	copy: wrote a.txt
13:04:22 DONE 	dry yes	copy: wrote a.txt
13:04:22 DONE 	force dry	copy: wrote a.txt
```

(the gaps around the labels are real tab characters in the output.)

The examples above assume a timestamp; with timestamps disabled the line simply begins at the level.

### Diff-only Interaction

The diff-only compressor measures the badged prefix in display columns, so its `〃` markers stay on the same tab stops with zero, one or several badges, and a changing badge set is handled per record by that record's own prefix. Two further rules apply to diff-only output regardless of badges:

- Multi-line messages: line *k* is compared with line *k* of the earlier messages; only line 1 follows the prefix, later lines start at column 0.
- Long lines: when a physical line's rendered, uncompressed width, badges and tab stops included, exceeds 100 columns, its dittos are separated by a space instead of a tab.

## API Sketch

```python
log.set_badges(["dry", "chk"])                    # every later record
log.done("...", badges=["dry", "force"])          # this record only
log.done("...", badges="deploy")                  # str or list of str

log.set_badges()                                  # unset all, same as None
log.set_badges(None)                              # unset all
log.set_badges([])                                # unset all, empty iterable
log.clear_badges()                                # unset all, explicit form
log.done("...", inherit_badges=False)             # this record: run-wide off
```

- `badges`: a `str` or an iterable of `str`, printed as bare labels, sorted by priority; there is no enum and no registry, so a custom badge needs no declaration.
- `set_badges`: replaces the run-wide set; a per-call `badges` is added to it for that record.
- Unsetting: `set_badges` with no argument, `None` or an empty iterable is the same as `clear_badges()`, and drops the whole run-wide set. There is no add or remove of a single label: to change the set, call `set_badges` with the full new list. `inherit_badges=False` hides the run-wide set for one record only, leaving it intact.
- Duplicates: a label is kept once, however often it is given.
- Custom badge default: grey, with priority `0`, after every native badge; custom badges keep the order given among themselves.
- Native labels: the names in the tables below get their defined hue; nothing validates them, so a typo prints as a grey custom badge.
- No conflict checking: kamilog is a log wrapper, so contradictory combinations are printed as given.

## Native Badges

What operation mode the current run is in. Priority is an integer, and the higher value prints earlier, so the most serious mode leads.

### Effect

| Badge | Color | Priority | CLI analogue | Reads as |
| --- | --- | --- | --- | --- |
| `dry` | bright yellow | 45 | `--dry-run`, `rsync -n` | nothing is changed, only reported |
| `chk` | yellow | 44 | `ansible --check`, `black --check` | state verified, not modified |
| `mock` | yellow | 43 | stubbed or fake backend | the action hit a stand-in, not the real system |
| `sbx` | green | 33 | `docker run --rm`, throwaway environment | the run is isolated, so nothing outlives it |

### Safety

| Badge | Color | Priority | CLI analogue | Reads as |
| --- | --- | --- | --- | --- |
| `force` | red | 52 | `-f`, `git push --force` | guards were bypassed |
| `undo` | red | 51 | `--rollback` | a prior run is being reversed |
| `unsafe` | bright red | 53 | `git --no-verify`, `curl -k` | verification was skipped |

### Prompting

| Badge | Color | Priority | CLI analogue | Reads as |
| --- | --- | --- | --- | --- |
| `yes` | yellow | 42 | `-y`, `apt -y` | prompts were auto-answered |
| `auto` | blue | 13 | `--non-interactive`, CI, cron | no human is present |

### Error Policy

| Badge | Color | Priority | CLI analogue | Reads as |
| --- | --- | --- | --- | --- |
| `strict` | green | 32 | `--strict`, `-Werror` | warnings count as failures |
| `keep` | yellow | 41 | `make -k`, `--continue-on-error` | failures logged, run continues |
| `fast` | green | 31 | `pytest -x`, `set -e` | the first failure stops the run |
| `retries` | cyan | 25 | `curl --retry`, `--retries N` | failed steps are attempted again |

### Execution

| Badge | Color | Priority | CLI analogue | Reads as |
| --- | --- | --- | --- | --- |
| `resm` | cyan | 24 | `wget -c`, `rsync --partial` | continuing an interrupted run |
| `new` | cyan | 23 | `--no-cache`, `--fresh` | previous state ignored, starting over |
| `offl` | cyan | 22 | `pip --no-index`, `npm --offline` | no network, cached data only |
| `incr` | cyan | 21 | `rsync`, only changed items | only what changed is processed |
| `watch` | blue | 12 | `--watch` | re-runs on change |
| `bg` | blue | 11 | `docker -d`, `&` | the run is detached from the terminal |
