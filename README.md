# kamilog README

A lightweight Python logging wrapper with structured output, custom log levels, ANSI 16-color support, and flexible timestamp options.

<!--
todo add file handler option for getLogger
todo comprehensive unit tests
todo allows use -V being equivalent to -vvv (v.v.)
todo allows to use only -V, dont add -v (v.v.)
todo smart time print
Bug using different logger to print & diff only can produce confusing result
Todo using pyproject.toml
-->

## Features

- **Custom log levels** — `ENTER` (11), `SKIP` (12), `SUCC` (15), `PASS` (21), `DONE` (25), `FAIL` (45) for hook and test-case workflows
- **Structured output** — `LEVEL source: message` with padded 5-char level names
- **ANSI 16-color output** — per-level colors, auto-disabled when output is piped
- **stdout/stderr split** — `< WARNING` goes to stdout, `>= WARNING` goes to stderr
- **Optional timestamps** — disable by default; enable with `datefmt=kamilog.DATEFMT_TIME` or `relative_to=`
- **Level constants** — `kamilog.DEBUG`, `kamilog.WARNING`, etc. — no `import logging` needed
- **Diff-only output** — repeated log lines compressed to show only what changed; common character runs replaced with `〃\t` markers, auto-applied to every logger
- **Verbosity helpers** — `-v`/`-q` CLI flags mapped to logging levels
- **Drop-in compatible** — `kamilog.getLogger()` in place of `logging.getLogger()`

---

See [docs/install_guide.md](docs/install_guide.md) for installation instructions.

See [docs/usage_doc.md](docs/usage_doc.md) for full usage documentation.

See [examples/](examples/) for runnable scripts demonstrating each feature.
