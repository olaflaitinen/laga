# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Repository cleanup, documentation refresh, and GitHub workflow improvements.
- Root ignore file for Python build and cache artifacts.
- Project ownership metadata updated for the `olaflaitinen` repository.

## [0.1.0] - 2026-07-24

### Added

- Fast path through `json.loads` for valid JSON.
- Recovery for comments, fences, prose, smart quotes, single quotes, missing commas, trailing commas, and truncated braces.
- `repair`, `repair_to_str`, and `loads` public entry points.
- Type information distributed through `py.typed`.
