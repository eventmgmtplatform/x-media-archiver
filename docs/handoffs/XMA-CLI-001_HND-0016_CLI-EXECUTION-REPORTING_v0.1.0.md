# HND-0016 — CLI execution reporting v0.1.0

Status: `CLI_REPORTING_OFFLINE_VALIDATED / PUBLIC_ACCEPTANCE_PENDING`

## Baseline and authorization

- Repository: `eventmgmtplatform/x-media-archiver`.
- Base: `main` at `30df8b9f93a78f6b5fec428b2cdabf50753a3944`.
- Baseline tree: `4605bebf519c92925ead958dc4c8d944a17458ae`.
- Baseline CI: run `41030869561`, `SUCCESS`, 451 tests, 90.91% coverage.
- Branch: `feature/xma-cli-execution-reporting`.
- Human authorization: PRM-0056 v0.1.0; offline implementation only.

## Design and contract

Presentation-independent typed DTOs build a compact `ExecutionReport` for `download`, `archive`,
and offline `status`. Human rendering reports public account identity, request semantics, execution
counts, completion, durable checkpoint, sanitized reason, and resumability. Exactly one new video
adds only that artifact's public metadata, size, digest, and repository-relative path. No-op and
aggregate executions do not misrepresent an old artifact as newly downloaded.

JSON success preserves every historical top-level key and adds `report` with
`report_schema_version=1`. JSON failures preserve the established exit code, leave stdout empty,
and emit one sorted, sanitized report to stderr. When durable progress cannot be read, fields remain
null with `progress_available=false`; counts are never invented.

Stable classifications retain the existing matrix: `INVALID_INPUT` (2), `PROVIDER_RESTRICTED`
(3), `PROVIDER_RATE_LIMITED` (4), `PROVIDER_FAILED`/`UNEXPECTED_FAILURE` (5), `CATALOG_FAILED`
(6), `NOT_FOUND` (7), `PROVIDER_TRANSIENT` (8), and `DOWNLOAD_FAILED` (9).

## Privacy and compatibility

The implementation does not expose cookies, Firefox selectors, personal or absolute paths, signed
media URLs, headers, tokens, contact data, tracebacks, or raw library exceptions. Artifact paths are
repository-relative. Commands, flags, success/failure semantics, JSON keys, download limits,
archive ALL/BOUNDED behavior, terminal idempotency, provider exhaustion, and offline status remain
compatible. SQLite schema, migrations, dependencies, `uv.lock`, workflows, discovery, IPC,
authentication, and downloader behavior are unchanged.

## Verification

Offline tests cover single/new, additive, no-op, aggregate, SINGLE_POST, bounded and ALL archive,
safety cap, provider exhaustion, terminal no-op, durable failures, unavailable progress, stable JSON
ordering, privacy negatives, and legacy regressions. The final command matrix, exact test count,
coverage, build result, commit/tree, and CI URL are recorded in the draft PR evidence because a
handoff cannot contain its own Git object identifier without becoming self-referential.

- `uv sync --locked --all-groups`: PASS.
- `uv run ruff format --check .`: PASS (193 files).
- `uv run ruff check .`: PASS.
- `uv run mypy`: PASS (46 source files).
- `uv run pytest`: PASS (463 tests, 90.35% total coverage).
- `uv build`: PASS (wheel and sdist for `0.2.0.dev0`).
- `git diff --check`: PASS.
- `uv.lock`, SQLite schema/migrations, dependencies, workflows, and operational limits: unchanged.

No X, Firefox, cookies, real multimedia repository, or public acceptance was accessed. Rollback is
the removal of the additive reporting module/rendering and additive manifest metadata fields; no
data migration is required.
