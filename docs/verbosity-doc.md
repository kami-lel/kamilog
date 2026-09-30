# Verbosity and Logging Level Documentation

Built-in helpers map verbosity, from either CLI flags or a plain integer, to
logging levels. The levels are described in the
[logging documentation](log-doc.md#custom-log-levels).













## CLI Flags

Add `-v`/`--verbose` and `-q`/`--quiet` to a parser:

```python
from argparse import ArgumentParser
import kamilog

parser = ArgumentParser()
kamilog.add_verbose_arguments(parser)
```

After parsing, apply the verbosity to a logger with
`set_logging_level_by_namespace`:

```python
args = parser.parse_args()

# target the root logger
kamilog.set_logging_level_by_namespace(args)

# target a named logger by name
kamilog.set_logging_level_by_namespace(args, logger_name="myapp")

# pass a logger instance directly (takes priority over logger_name)
log = kamilog.getLogger("myapp")
kamilog.set_logging_level_by_namespace(args, logger=log)
```

Pass `verbosity` to shift the base level that `-v`/`-q` counts are added
to/subtracted from, instead of starting from `0`:

```python
# start two steps quieter, then apply -v/-q on top
kamilog.set_logging_level_by_namespace(args, verbosity=-2)
```













## Verbosity Integer

To set the level from a verbosity integer directly, without a parsed
`argparse` namespace, use `set_logging_level_by_verbosity`:

```python
# positive raises detail, negative lowers it
kamilog.set_logging_level_by_verbosity(2)

kamilog.set_logging_level_by_verbosity(2, logger_name="myapp")

log = kamilog.getLogger("myapp")
kamilog.set_logging_level_by_verbosity(2, logger=log)
```













## Verbosity-to-Level Mapping

| Flags | Verbosity | Level | Number | Shows |
|---|---|---|---|---|
| `-vvv` or more | ≥ 3 | `DEBUG` | 10 | DEBUG, 〃 |
| `-vv` | 2 | `ENTER` | 15 | ENTER, SKIP, SUCC, 〃 |
| `-v` | 1 | `INFO` | 20 | INFO, PASS, 〃 |
| *(none)* | 0 | `DONE` | 25 | DONE, 〃 |
| `-q` | -1 | `WARN` | 30 | WARN, 〃 |
| `-qq` | -2 | `ERROR` | 40 | ERROR, FAIL, 〃 |
| `-qqq` or more | ≤ -3 | `CRIT` | 50 | CRIT |













## Calculation Only

`set_logging_level_by_namespace` and `set_logging_level_by_verbosity` set a
logger's level as a side effect. To get the offset or the level back as a
plain value instead — for logging, testing, or passing along elsewhere — use
`calc_verbosity` and `calc_logging_level` directly:

```python
# apply a namespace's -v/-q counts to a base verbosity, without touching a logger
verbosity = kamilog.calc_verbosity(args, verbosity=-2)

# map a verbosity integer to a logging level
level = kamilog.calc_logging_level(2)  # ENTER

# or fold a namespace's offset into the same call
level = kamilog.calc_logging_level(-2, namespace=args)
```

`set_logging_level_by_namespace(args, verbosity=v)` is equivalent to
`logger.setLevel(kamilog.calc_logging_level(v, namespace=args))`.
