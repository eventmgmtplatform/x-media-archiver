# X Media Archiver 0.1.0

Local-first Linux CLI for discovering, cataloging and downloading bounded public video from X into
a normalized repository with SQLite metadata, sidecars and integrity hashes.

## Version status

Version 0.1.0 is the first published bounded Linux distribution. Install from the immutable
`v0.1.0` GitHub Release and verify the distributed checksums; moving branches are development
sources, not releases. The supported maximum is ten
videos and the product is not certified for bulk operation.

## Supported platforms

Linux x86_64 is supported. Ubuntu 22.04 and 24.04 are release-candidate test targets. Windows and
macOS are not certified. A local filesystem with `flock` is required for durable archive locking.

## Installation

Recommended release bundle:

```bash
tar -xzf xma-v0.1.0-linux-x86_64.tar.gz
cd xma-v0.1.0-linux-x86_64
./xma --help
./xma version
```

The bundle does not require a system Python or uv.

Advanced source installation:

```bash
git clone https://github.com/eventmgmtplatform/x-media-archiver.git
cd x-media-archiver
git checkout --detach v0.1.0
uv sync --locked --all-groups
uv run xma version
```

Advanced wheel installation uses the locally built `x_media_archiver-0.1.0-py3-none-any.whl` in an
isolated Python 3.12 environment. See the local CLI runbook.

## Quick start

Firefox authentication is optional for commands that can operate anonymously and explicit for a
local authenticated session. Pass only the contained Firefox profile name; never export cookies.

```bash
xma download @HANDLE --limit 1 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME
xma download @HANDLE --limit 2 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME
xma download @HANDLE --limit 5 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME

xma archive @HANDLE --limit 10 --batch-size 2 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME \
  --request-interval 2 --discovery-timeout 30

xma download "https://x.com/HANDLE/status/POST_ID" --limit 1 \
  --repository ./repository-single \
  --auth-browser firefox --auth-profile PROFILE_NAME
```

Use `uv run xma` instead of `xma` when operating from source.

## Repository and resumption

The normalized repository contains a SQLite catalog, media artifacts, JSON sidecars and manifests.
Completed artifacts are deduplicated and never overwritten. Archive checkpoints are committed only
after persisted pages. Inspect state without network access:

```bash
xma status --repository ./repository-HANDLE
xma status --repository ./repository-HANDLE --json
```

`COMPLETED` means the requested total is present. `PAUSED` preserves valid progress for controlled
resumption. `FAILED` requires integrity diagnosis before another run. Back up the entire repository,
not only SQLite.

## Security

- Cookie values are read through the contained Firefox read-only boundary and are not exported.
- Signed media URLs, headers, tokens and local profile paths are not persisted.
- Authentication fails closed when required session cookies are absent.
- Downloads stage to `.part`, validate size/SHA-256 and move atomically.
- Never commit repositories, SQLite databases, logs, cookies, media or release artifacts.

Report vulnerabilities according to [SECURITY.md](SECURITY.md).

## Known limitations

- Maximum ten videos; no certified bulk or unattended operation.
- `RESCAN_DEDUP_V1` rescans and deduplicates; it is not an efficient remote cursor for thousands.
- No scheduler, daemon, GUI, API service, Redis, Docker runtime, yt-dlp or FFmpeg integration.
- Provider availability and authenticated X behavior can change independently of XMA.
- Verify the `v0.1.0` tag and `SHA256SUMS`; do not install an arbitrary moving branch.

## Documentation

- [Product wiki](docs/wiki/index.md)
- [System requirements](docs/requirements/XMA-CLI-001_SYSTEM-REQUIREMENTS_v1.0.0.md)
- [BAU operations](docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md)
- [Local CLI runbook](docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md)
- [Architecture](docs/architecture/XMA-CLI-001_ARCHITECTURE_v0.1.0.md)
- [Release management](docs/release/XMA-CLI-001_RELEASE-MANAGEMENT_v1.0.0.md)
- [Release checklist](docs/release/XMA-CLI-001_RELEASE-CHECKLIST_v1.0.0.md)
- [Historical governance, prompts, audits and handoffs](docs/)

License: GPL-2.0-only. Third-party composition is documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
