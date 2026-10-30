# X Media Archiver 0.2.0.dev0

Local-first Linux CLI for discovering, cataloging and downloading bounded public video from X into
a normalized repository with SQLite metadata, sidecars and integrity hashes.

## Version status

Version 0.1.2 is the current published release. Interactive download and durable archive enforce a
repository maximum of twenty videos. The release remains intentionally bounded and is not
certified for bulk or unattended operation.

The current development branch adds an `archive --all` contract validated with observations on one
public account. It does not change the published v0.1.2 guarantee and is not certified for mass or
unattended operation.

## Supported platforms

Linux x86_64 is supported. Ubuntu 22.04 and 24.04 are validated release targets. Windows and
macOS are not certified. A local filesystem with `flock` is required for durable archive locking.

## Installation

Recommended release bundle:

Download the published v0.1.2 assets, verify `SHA256SUMS`, and extract the standalone bundle:

```bash
tar -xzf xma-v0.1.2-linux-x86_64.tar.gz
cd xma-v0.1.2-linux-x86_64
./xma --help
./xma version
```

The published bundle does not require a system Python or `uv`.

Advanced source installation:

For source validation, check out the immutable published tag:

```bash
git clone https://github.com/eventmgmtplatform/x-media-archiver.git
cd x-media-archiver
git checkout --detach v0.1.2
uv sync --locked --all-groups
uv run xma version
```

Advanced wheel installation uses the locally built `x_media_archiver-0.1.2-py3-none-any.whl` in an
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
xma download @HANDLE --limit 10 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME
xma download @HANDLE --add 1 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME
xma download @HANDLE --add 5 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME

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

Development-only complete-profile syntax and safety semantics are documented in
[`docs/operations/XMA-CLI-001_B06-ARCHIVE-ALL-RUNBOOK_v0.1.0.md`](docs/operations/XMA-CLI-001_B06-ARCHIVE-ALL-RUNBOOK_v0.1.0.md).
Use `--all` only with a safety cap. Typed provider exhaustion produces a completed, non-resumable
run and a manifest with `complete=true` and `exhausted=true`; reaching the cap produces a resumable
`PAUSED / SAFETY_CAP_REACHED` state. `status` remains completely offline.

## Security

- Cookie values are read through the contained Firefox read-only boundary and are not exported.
- Signed media URLs, headers, tokens and local profile paths are not persisted.
- Authentication fails closed when required session cookies are absent.
- Downloads stage to `.part`, validate size/SHA-256 and move atomically.
- Never commit repositories, SQLite databases, logs, cookies, media or release artifacts.

Report vulnerabilities according to [SECURITY.md](SECURITY.md).

## Known limitations

- Download accepts absolute `--limit 1..10` or additive `--add 1..20`; the resulting verified total
  cannot exceed twenty in v0.1.2; `--add` accepts 1..20. Durable `archive` is also capped at twenty.
- No certified bulk or unattended operation.
- `RESCAN_DEDUP_V2` rescans and deduplicates; it is not an efficient remote cursor for thousands.
- No scheduler, daemon, GUI, API service, Redis, Docker runtime, yt-dlp or FFmpeg integration.
- Provider availability and authenticated X behavior can change independently of XMA.
- Verify the published `SHA256SUMS` and `RELEASE-MANIFEST.json` before installation.

## Documentation

- [Product wiki](docs/wiki/index.md)
- [B06 complete-profile archive](docs/wiki/b06-complete-profile-archive.md)
- [System requirements](docs/requirements/XMA-CLI-001_SYSTEM-REQUIREMENTS_v1.0.0.md)
- [BAU operations](docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md)
- [Local CLI runbook](docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md)
- [Architecture](docs/architecture/XMA-CLI-001_ARCHITECTURE_v0.1.0.md)
- [Release management](docs/release/XMA-CLI-001_RELEASE-MANAGEMENT_v1.0.0.md)
- [Release checklist](docs/release/XMA-CLI-001_RELEASE-CHECKLIST_v1.0.0.md)
- [Historical governance, prompts, audits and handoffs](docs/)

License: GPL-2.0-only. Third-party composition is documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
