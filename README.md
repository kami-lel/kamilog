# kamilog README

A lightweight Python logging wrapper with structured output, custom log levels, combinable ANSI color styling, and flexible timestamp options.

<!--
todo add file handler option for getLogger
Todo allows use -V being equivalent to -vvv (v.v.)
todo smart time print
todo cli logger: implement relative time
todo cli logger: allow to use already set up logger
bug using different logger to print & diff only can produce confusing result
-->

## Features

#### 🎯 Custom Logging Experience

- Eleven custom log levels (`ENTER`, `SKIP`, `SUCC`, `PASS`, `NOTE`, `TIP`, `DONE`, `HINT`, `IMPORTANT`, `CAUTION`, `FAIL`) for test, hook, and general-purpose workflows
- Structured output with padded level names
- Automatic stdout/stderr split by severity
- Diff-only compression for repeated log lines
- Drop-in replacement for `logging.getLogger()`

#### 🎨 ANSI Colored Output

- Per-level ANSI formatting with bold
- Combinable `AnsiStyle` flags — foreground, background, bold, and underline, mixed freely with `|`
- Triage-tag coloring via `color_triage_tag`
- TTY-aware (auto-disabled when piped)
- Public color API for custom colored output

#### ⚡ Verbosity Control

- `-v`/`-q` CLI argument helpers
- Seven verbosity steps from `CRITICAL` to `DEBUG`

#### 📐 Comment Banner Utilities

- Centered, left-justified, and right-justified alignment modes
- Fixed-width terminal banners with custom fill characters
- Horizontal offset for centered banners, keeping titles aligned behind a prefix

#### 💻 Command-Line Interface

- Subcommands for comment banners (`cb`, `cb0`) and logging (`logger`)
- Each subcommand carries comprehensive `-h`/`--help` text — the de facto CLI reference
- Run `python kamilog/kamilog.py -h` to list subcommands, then `python kamilog/kamilog.py <subcommand> -h` for its full options

---

Q.v. [docs/install_guide.md](docs/install_guide.md) for installation instructions.

Q.v. [docs/usage_doc.md](docs/usage_doc.md) for full usage documentation.

Q.v. [examples/](examples/) for runnable scripts demonstrating each feature.
