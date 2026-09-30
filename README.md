# kamilog

A lightweight Python logging wrapper with structured output, custom log levels, combinable ANSI color styling, and flexible timestamp options.













## Features

#### 🎯 A Logger That Actually Tells a Story

Standard `logging` flattens everything into `DEBUG`/`INFO`/`WARNING`/`ERROR`.
kamilog adds eleven more levels — `ENTER`, `SKIP`, `SUCC`, `PASS`, `NOTE`,
`TIP`, `DONE`, `HINT`, `IMPORTANT`, `CAUTION`, `FAIL` — so a log reads like
the narrative of a run, not just a severity dump. It's a drop-in swap for
`logging.getLogger()`, so nothing else in your codebase has to change.

#### 🎨 Color That Earns Its Keep

Every level gets its own bold ANSI color out of the box, and colors
combine freely for anything custom. It's TTY-aware, so piping output to a
file or another process never leaves you with escape-code garbage.

#### ⚡ Verbosity Without the Boilerplate

`-v`/`-q` flags and seven verbosity steps come for free — no more hand-
rolling the same `argparse` glue in every project.

#### 🏷️ Badges for the Mode of a Run

Tag a whole run as `dry`, `force`, `auto`, or any custom label with
`set_badges()`, and every line shows it before the level, colored by
severity. Repeated lines still compress cleanly, multi-line messages
included. Q.v. the [badges documentation](docs/badge-doc.md) for every
native badge and how to set them.

#### 📐 Terminal Banners, Done Right

Clean, fixed-width section banners with centered, left-, or right-justified
titles — the kind of visual structure that makes long CLI output and log
files scannable instead of a wall of text.

#### 💻 A CLI, Not Just a Library

`kamilog` installs as its own shell command, ready to use without writing
a line of Python.













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

Q.v. [docs/usage_doc.md](docs/usage_doc.md) for full usage documentation.

Run `kamilog -h` for the full CLI reference — each subcommand's `-h`/`--help` text is the de facto documentation.

Q.v. [examples/](examples/) for runnable scripts demonstrating each feature.
