# kamilog CHANGELOG

[^format]
















## [Unreleased]

### Added

- `AGENTS.md` with contributor and agent guidelines
- `docs/install_guide.md` — installation guide (extracted from README)
- `docs/usage_doc.md` — usage documentation (extracted from README)
- export `add_verbose_arguments`, `calc_verbosity`, `set_logging_level_by_verbosity` via `__all__`
- custom log levels: `ENTER` (11), `SKIP` (12), `PASS` (25), `FAIL` (45)
- `KamiLogger` subclass of `logging.Logger` with `.enter()`, `.skip()`, `.pass_()`, `.fail()` methods
- `KamiLogger` exported via `__all__`
- ANSI 16-color output: datetime in black, level name colored per severity, message uncolored
- color is auto-disabled when stdout/stderr is not a TTY (piped or redirected)
- separate stdout handler (below `WARNING`) and stderr handler (`WARNING` and above)

### Changed

- improve help message for verbosity arguments
- `getLogger()` now always returns a `KamiLogger` instance; upgrades pre-existing loggers via `__class__` assignment
- `_PADDED_LEVELNAME_MAP` moved to module level
- log record is copied before formatting to prevent mutation of the shared record across handlers

### Deprecated
### Removed
### Fixed

[unreleased]: https://github.com/kami-lel/kami-log-py/compare/v1.2.0...dev













## [1.2.0] - 2025-10-01

### Added

- function related to verbosity and logging levels

  - related tests

[1.2.0]: https://github.com/kami-lel/kami-log-py/compare/v1.1.0...v1.2.0













## [1.1.0] - 2025-09-10

### Added

- Installation as Module feature

[1.1.0]: https://github.com/kami-lel/kami-log-py/compare/v1.0.0...v1.1.0

















## [1.0.0] - 2025-09-10

### Added

- basic function implemented in `kamilog.py`

[1.0.0]: https://github.com/kami-lel/kami-log-py/releases/tag/v1.0.0













[^format]: CHANGELOG format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); Version scheme adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).