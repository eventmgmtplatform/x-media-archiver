# XMA-CLI-001 system requirements v1.0.0

## Supported environment

- Linux x86_64; Ubuntu 22.04 and 24.04 are tested release-candidate platforms.
- Local filesystem supporting POSIX atomic rename and `fcntl.flock`.
- Write access to the normalized repository and sufficient disk space.
- HTTPS connectivity to X for explicitly requested public operations.
- For authenticated operation, Firefox under the same Linux user, an authenticated contained
  profile, and read permission on its cookie database. Cookies are never exported.

Windows and macOS are not certified. There is no scheduler, daemon, bulk-download service or
supported maximum above ten videos.

## Capacity

Estimate free space as `sum(expected media bytes) × 1.2 + 100 MiB`. The multiplier covers staging,
sidecars, manifests, SQLite and filesystem overhead. Keep additional capacity for backups.

## Installation variants

The Linux bundle needs no external Python. Wheel/source installation needs Python 3.11+ (Python
3.12 is used for release builds), uv for locked source environments, and native HTTPS certificate
support. All production dependencies must match `uv.lock`.

## Repository compatibility

SQLite schema version 2 is current. Migrations are monotonic and preserve version 1 B02–B04
catalogs. Back up the complete repository before upgrading. A newer schema fails closed; catalog,
filesystem, sidecar, size and SHA-256 inconsistencies must be resolved before resumption.
