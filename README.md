# kamilog

A lightweight Python logging wrapper with structured output, custom log levels, combinable ANSI color styling, and flexible timestamp options.













## Features

#### 🎯 A Logger That Actually Tells a Story

Standard `logging` flattens everything into `DEBUG`/`INFO`/`WARNING`/`ERROR`.
kamilog adds eleven more levels — `ENTER`, `SKIP`, `SUCC`, `PASS`, `NOTE`,
`TIP`, `DONE`, `HINT`, `IMPORTANT`, `CAUTION`, `FAIL` — so a log reads like
the narrative of a run, not just a severity dump. It's a drop-in swap for
`logging.getLogger()`, so nothing else in your codebase has to change. Levels,
timestamps, repeated-line compression, and file output are covered in the
[logging documentation](docs/log-doc.md).

#### 🎨 Color That Earns Its Keep

Every level gets its own bold ANSI color out of the box, and colors
combine freely for anything custom. It's TTY-aware, so piping output to a
file or another process never leaves you with escape-code garbage. Use the
same colors outside logging through the [ANSI documentation](docs/ansi-doc.md).

#### ⚡ Verbosity Without the Boilerplate

`-v`/`-q` flags and seven verbosity steps come for free — no more hand-
rolling the same `argparse` glue in every project. The
[verbosity documentation](docs/verbosity-doc.md) shows how flags map to levels.

#### 🏷️ Badges for the Mode of a Run

Tag a whole run as `dry`, `force`, `auto`, or any custom label with
`set_badges()`, and every line shows it before the level, colored by
severity. Repeated lines still compress cleanly, multi-line messages
included. Q.v. the [badges documentation](docs/badge-doc.md) for every
native badge and how to set them.

#### 📝 Deeds: One Line per Thing Done

Log creating, copying, deleting, downloading, and running as fixed, readable
lines, and let a failure log itself with its error. Q.v. the
[deeds documentation](docs/deed-doc.md) for every deed and the failure
handling.

#### 📐 Terminal Banners, Done Right

Clean, fixed-width section banners with centered, left-, or right-justified
titles — the kind of visual structure that makes long CLI output and log
files scannable instead of a wall of text. Q.v. the
[banner documentation](docs/banner-doc.md).

#### 💻 A CLI, Not Just a Library

`kamilog` installs as its own shell command, ready to use without writing
a line of Python. Scripts that may run where `kamilog` is missing can carry
the [shell shim](docs/shim-doc.md), which keeps them working either way.













## Install

#### Package Install

Install via `pip`. This also registers the `kamilog` shell command (`console_scripts` entry point) automatically.

Clone and install:

```bash
git clone https://github.com/kami-lel/kamilog.git
cd kamilog
pip install .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/kami-lel/kamilog.git
```

#### Copy Install

Embed kamilog directly into your project, no `pip` required.

Copy the single file into your project root:

```
your_project/
├── kamilog.py
└── main.py
```

Or copy the entire folder into your project's source directory:

```
your_project/
├── project_abc/
│   ├── kamilog/
│   │   ├── __init__.py
│   │   └── kamilog.py
│   ├── module_a/
│   └── module_b/
└── pyproject.toml
```













## Usage

Start with the [logging documentation](docs/log-doc.md), then pick the topic
you need:

- Levels, Timestamps & Files: [logging](docs/log-doc.md)
- Run Modes: [badges](docs/badge-doc.md), shown on every line
- Common Actions: [deeds](docs/deed-doc.md), logged in fixed wording
- `-v`/`-q` Flags: [verbosity](docs/verbosity-doc.md)
- Colors Without Logging: [ANSI output](docs/ansi-doc.md)
- Section Banners: [comment banners](docs/banner-doc.md)
- Shell Scripts Without kamilog: [shim](docs/shim-doc.md)

Run `kamilog -h` for the full CLI reference — each subcommand's `-h`/`--help` text is the de facto documentation.

Q.v. [examples/](examples/) for runnable scripts demonstrating each feature.
