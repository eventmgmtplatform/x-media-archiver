# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic
Versioning.

## [Unreleased]

### Added

- Sanitized media transport classifications, bounded URL renewal, additive downloads through 20,
  and an explicit opt-in public acceptance harness.

## [0.1.1] - 2026-10-29

### Added

- Additive interactive download through `--add 1..10`, bounded scanning and explicit
  provider-best quality metadata.

### Changed

- Interactive `download --limit` accepts every desired total from 1 through 10. Durable `archive`
  remains the checkpointed route and the global v0.1.1 maximum remains ten.

### Fixed

- Recover `FAILED_FINAL` jobs without artifacts or residue through an explicit audited retry.
- Treat lower absolute limits as successful offline no-ops without deleting completed artifacts.
- Remove failed staging residue and empty media-index directories.

### Security

- Reject invalid or additive totals above ten before provider/authentication/network construction.

### Known Limitations

- Interactive download and durable archive remain capped at ten; no mass-download certification.

## [0.1.0] - 2026-10-29

### Added

- Typed B02 domain contracts, SQLite schema migrations and transactional unit of work.
- Public discovery/catalog commands, bounded Firefox session authentication and sanitized errors.
- Profile and exact SINGLE_POST download, integrity sidecars, manifests and atomic staging.
- Durable archive/status with checkpoints, rate limiting, locking, reconciliation and resumption.
- Linux x86_64 standalone bundle, wheel, sdist, SBOM and release-candidate automation.

### Changed

- Consolidated validated B03–B05 snapshots onto a temporary release branch.
- Version metadata promoted from `0.1.0.dev0` to `0.1.0`.
- README and operations documentation now present current user workflows instead of rework history.

### Fixed

- Reconciled post-merge B02 identity parsing, migration timestamps, discovery-run progress and
  failed unit-of-work connection cleanup without regressing B03–B05.
- Preserved final candidates across worker termination and durable counts across archive resumes.

### Security

- Authentication remains read-only and fail-closed; cookies, signed URLs and raw provider errors
  are excluded from persistent/public output.
- Release validation scans dependencies, licenses, tracked secrets and forbidden local artifacts.
- The v0.1.0 distribution carries the complete GPL-2.0-only text and the verified corresponding
  source archive for gallery-dl 1.32.18.

### Distribution

- Added a self-contained quick start, README and operating runbooks to the standalone bundle.
- Added a versioned product wiki and GitHub Pages workflow for release and roadmap control.
- Added a sanitized `RELEASE-MANIFEST.json` and complete checksums for distributed assets without
  self-referential hashes.

### Known Limitations

- Maximum ten videos; no bulk certification, scheduler, daemon or efficient remote cursor.
- Linux x86_64 only; Windows and macOS are not certified.
- Provider availability remains external to XMA.

[Unreleased]: https://github.com/eventmgmtplatform/x-media-archiver/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/eventmgmtplatform/x-media-archiver/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.0
