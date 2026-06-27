# kamilog README

A lightweight Python logging wrapper with structured output, custom log levels, ANSI 16-color support, and flexible timestamp options.

<!--
Todo diff only printing is inconsistent
Fixme change verbosity assignment, default is equivalent to INFO
todo add file handler option for getLogger
todo install as submodule
todo comprehensive unit tests
-->

## Features

- **Custom log levels** — `ENTER` (11), `SKIP` (12), `PASS` (21), `SUCC` (22), `DONE` (25), `FAIL` (45) for hook and test-case workflows
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
