# Custom Logging Documentation

Use `kamilog.getLogger()` in place of `logging.getLogger()` to get a
ready-to-use logger with colored, compact output and extra log levels.

```python
import kamilog

log = kamilog.getLogger("myapp")
log.setLevel(kamilog.DEBUG)

log.debug("Debugging details here")
log.info("Informational message")

try:
    1 / 0
except ZeroDivisionError as err:
    log.exception(err)

log.enter("starting operation")
log.done("operation completed")
log.warning("Warning message")
```

Output:

```
DEBUG myapp: Debugging details here
INFO  myapp: Informational message
ERROR myapp: division by zero
Traceback (most recent call last):
  File "main.py", line 12, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
ENTER myapp: starting operation
DONE  myapp: operation completed
WARN. myapp: Warning message
```

> [!NOTE]
> Logger name (`myapp:`) is omitted when `name` is `None` or `"root"`.

Records below `WARNING` go to stdout, `WARNING` and above go to stderr.

Related guides: [verbosity](verbosity-doc.md) for `-v`/`-q` flags that set the
level, and the [README](../README.md) for installation.














## Custom Log Levels

On top of the standard levels, kamilog adds a set for scripts, tools and
tests. Every level has a method of the same name on the logger.

| Level | Num | Method | Color | Use it for |
|---|---|---|---|---|
| DEBUG | 10 | `.debug()` | cyan | internal state and control flow |
| ENTER | 15 | `.enter()` | bright cyan | entering a subroutine or test section |
| SKIP  | 16 | `.skip()` | bright cyan | a branch or test case that was skipped on purpose |
| SUCC. | 17 | `.succ()` | bright green | a subroutine finished successfully |
| INFO  | 20 | `.info()` | blue | a general event during normal execution |
| PASS  | 21 | `.pass_()` | green | a test assertion or case passed |
| NOTE  | 23 | `.note()` | bright blue | an aside worth recording |
| TIP   | 24 | `.tip()` | bright blue | an actionable suggestion |
| DONE  | 25 | `.done()` | bright green | the whole program or a major phase finished |
| HINT  | 26 | `.hint()` | magenta | a subtle cue on what to do |
| IMPT. | 27 | `.important()` | bright magenta | information that must stand out |
| WARN. | 30 | `.warning()` | yellow | something unexpected, but recoverable |
| CAUT. | 31 | `.caution()` | yellow | something needing prompt attention |
| ERROR | 40 | `.error()` | bright yellow | an operation failed |
| FAIL  | 45 | `.fail()` | red | a test assertion or case failed |
| CRIT. | 50 | `.critical()` | bright red | the program cannot continue |

> [!IMPORTANT]
> `.pass_()` uses a trailing underscore because `pass` is a Python keyword.

**Development logging: `DEBUG`, `ENTER`, `SKIP`, `SUCC.`.** These levels help a developer follow the structure and flow of ordinary execution, and none of them are meant for a production user. `DEBUG` traces internal state and control flow. `ENTER` marks the start of a major subroutine or section; pair it at the top with `SUCC.` on successful completion. `SKIP` marks the expected skip of a logic branch that was deliberately not taken.

**Test conditions: `ENTER`, `SKIP`, `PASS`, `FAIL`.** These track the flow of a test script and are likewise developer-facing, not for a production user. `ENTER` marks the start of a major test section. Each test-case branch then logs exactly one of `PASS` or `FAIL`: a passing assertion or a failing one. `SKIP` marks a test case that is deliberately not run.

**Production logging: `INFO`, `NOTE`, `TIP`, `DONE`.** These are addressed to the production user and can be expected to land in the production logs. `INFO` records a general event or state change during normal execution, while `NOTE` is a plainer aside worth keeping and `TIP` offers an actionable suggestion. `DONE` fires once, at the successful finish of an entire program or major phase. It is the production-facing counterpart to the developer-only `SUCC.`.

**Terminal attention: `HINT`, `IMPT.`, `CAUT.`.** These are expected to be printed to the terminal, so they usually point at something the user should actually do. `HINT` is the quietest of the three. `IMPT.` is emphasized information that should stand out. `CAUT.` escalates one step further, demanding even more immediate attention than `IMPT.`.

**Error escalation: `WARN.`, `ERROR`, `CRIT.`.** These form a ladder of increasing severity: a recoverable surprise, a failed operation, and an outright crash, logged in that order as a situation worsens.













## ANSI Color Output

Color is on automatically when the output is a terminal, and off when it is piped or
redirected to a file. To use the same colors outside logging, see the
[ANSI documentation](ansi-doc.md). To turn it off for good:

```python
log = kamilog.getLogger("myapp", disable_color=True)
```













## Timestamp Format

By default the console shows no timestamp and a log file gets the full date
and time with milliseconds. Pass `datefmt` to use one format for both, or
`None` to drop timestamps everywhere.

| Constant | Example |
|---|---|
| `DATEFMT_TIME` | `14:30:00 INFO  myapp: message` |
| `DATEFMT_TIME_MS` | `14:30:00.123 INFO  myapp: message` |
| `DATEFMT_DATETIME` | `2026-06-15 14:30:00 INFO  myapp: message` |
| `DATEFMT_DATETIME_MS` | `2026-06-15 14:30:00.123 INFO  myapp: message` |
| `None` | `INFO  myapp: message` |

```python
log = kamilog.getLogger("myapp", datefmt=kamilog.DATEFMT_TIME)
```

### Relative Time

Pass a Unix timestamp as `relative_to` to display the elapsed time since then,
on console and file alike. `datefmt` is ignored in this mode.

```python
import time

log = kamilog.getLogger("myapp", relative_to=time.time())
log.info("first message")   # +00:00:00.001 INFO  myapp: first message
```













## Diff-only Output

Diff-only output is on by default. Once a logger has printed three messages, the parts that stay the same from
one message to the next are collapsed into `〃` marks, so only what changed
stands out:

```
INFO  sensor: temperature=21.4 humidity=55% status=OK
INFO  sensor: te〃    ture=21.6 humidity=55% status=OK
INFO  sensor: te〃    ture=21.9 humidity=55% status=OK
```

Multi-line messages are compared line by line. Compression starts over
whenever the message pattern changes. To always print every line in full:

```python
log = kamilog.getLogger("myapp", disable_diff_only_compression=True)
```













## File Output

Pass `filename` to also write the log to a file. The file never contains
colors, and every level goes into the one file.

```python
log = kamilog.getLogger("myapp", filename="app.log")
```

- `disable_console=True`: write to the file only
- `file_mode`: how the file is opened, `"a"` appends (default), `"w"` starts
  it fresh on each run

Calling `getLogger()` again with the same name is safe and never prints a
message twice.
