# kamilog README

A lightweight Python logging wrapper with structured output, custom log levels, ANSI 16-color support, and flexible timestamp options.

<!--
todo add file handler option for getLogger
todo comprehensive unit tests for logger
todo allows use -V being equivalent to -vvv (v.v.)
todo allows to use only -V, dont add -v (v.v.)
todo smart time print
Todo logger as bash CLI
bug using different logger to print & diff only can produce confusing result
Bug parser need to private
-->

## Features

#### 🎯 Custom Logging Experience

- Six custom log levels (`ENTER`, `SKIP`, `SUCC`, `PASS`, `DONE`, `FAIL`) for test and hook workflows
- Structured output with padded level names
- Automatic stdout/stderr split by severity
- Diff-only compression for repeated log lines
- Drop-in replacement for `logging.getLogger()`

#### 🎨 ANSI Colored Output

- Per-level 16-color ANSI formatting with bold
- TTY-aware (auto-disabled when piped)
- Public color API for custom colored output

#### ⚡ Verbosity Control

- `-v`/`-q` CLI argument helpers
- Seven verbosity steps from `CRITICAL` to `DEBUG`

#### 📐 Comment Banner Utilities

- Centered, left-justified, and right-justified alignment modes
- Fixed-width terminal banners with custom fill characters

#### 💻 Command-Line Interface

- Built-in CLI for comment banner via `python kamilog/kamilog.py cb`
- Support for short and long mode aliases
- Customizable output width and destination (stdout/stderr)

---

Q.v. [docs/install_guide.md](docs/install_guide.md) for installation instructions.

Q.v. [docs/usage_doc.md](docs/usage_doc.md) for full usage documentation.

Q.v. [examples/](examples/) for runnable scripts demonstrating each feature.
