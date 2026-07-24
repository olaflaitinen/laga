# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Repository citation metadata and README citation guidance.

## [0.1.5] - 2026-07-24

### Added

- Version bump and documentation alignment for the 0.1.5 release.

## [0.1.4] - 2026-07-24

### Added

- File-based repair helper, CLI file input/output support, and compact/pretty output controls.
- Line-and-column context in error messages for easier debugging.
- README and API guidance for choosing between `json.loads`, `repair`, and `repair_file`.

### Changed

- Expanded usage docs, API docs, and release notes to match the new CLI and helper surface.

## [0.1.3] - 2026-07-24

### Added

- Expanded issue forms for bug reports, feature requests, usage questions, and documentation feedback.
- More detailed repository metadata with a project contact email.
- Release-prep guidance for the next version line.

### Changed

- Updated package metadata and citation records for the 0.1.3 update package.

## [0.1.2] - 2026-07-24

### Added

- CLI stdin support, pretty output, and explicit input control flags.
- Configurable input size, nesting depth, and duplicate-key handling.
- Richer error context for malformed inputs.

### Changed

- Improved the default developer experience around malformed JSON repair and CLI usage.

## [0.1.1] - 2026-07-24

### Added

- Repository cleanup, documentation refresh, and GitHub workflow improvements.
- Root ignore file for Python build and cache artifacts.
- Project ownership metadata updated for the `olaflaitinen` repository.

### Changed

- Dropped Python 3.9 support; laga 0.1.1 targets Python 3.10 through 3.13.

## [0.1.0] - 2026-07-24

### Added

- Fast path through `json.loads` for valid JSON.
- Recovery for comments, fences, prose, smart quotes, single quotes, missing commas, trailing commas, and truncated braces.
- `repair`, `repair_to_str`, and `loads` public entry points.
- Type information distributed through `py.typed`.
