# HND-0015 — B06 cap-50 acceptance blocked v0.4.0

Status: `REWORK_REQUIRED`

## Authorization and baseline

- Authorization: PRM-0050, exactly one resume toward operational cap 50.
- Baseline head/tree: `78290d0fd44f6a5279df7090535533f3730c18cf` /
  `3604868f0ace01aa93282848846073326626a2aa`.
- Baseline CI: 41002592091, SUCCESS; 437 tests; 90.59% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Initial repository: 20 verified artifacts, page/checkpoint 4/4, safety-cap pause, aggregate hash
  `583dd44193c2d2fec37470a0cfcec9ddeba0989d9e25a6e199a3b594c8f61168`.

Target, profile, paths, cookies, tokens, headers, URLs, query strings, account data, and raw logs
remain private and are represented only as `<LOCAL_TARGET>`, `<LOCAL_PROFILE>`, and
`<LOCAL_B06_REPOSITORY>`.

## Single execution and defect

- Command count: one; retry/inspect count: zero.
- Exit code/duration: 2 / 0 seconds.
- Progress: 20→20; no discovery, candidate, or download occurred.
- Final run: `FAILED / DomainError`, page/checkpoint 4/4, failed total 0, cap recorded as 50.
- Sanitized classification: the first absolute page target would be 25, but DownloadService
  reconstructs `manifest_request` without `archive_all=True`; the interactive download validation
  rejects totals above 20 before provider access.

The run never remained RUNNING. This is a functional boundary defect requiring a new governed
rework; PRM-0050 prohibited correcting it or retrying the command.

## Preserved evidence

- Videos/sidecars/artifacts/completed jobs/distinct identities: 20/20/20/20/20.
- SQLite integrity and catalog/filesystem/hash/size/sidecar reconciliation: PASS.
- All twenty initial hashes remained byte-identical; aggregate hash unchanged.
- Zero `.part` and `.tmp`; lock released.
- Available space: 23,653,134,336 bytes before and 23,652,102,144 bytes after diagnosis.
- The exact repository remains retained under `<LOCAL_B06_REPOSITORY>`.

## Offline validation and CI

- Locked sync, Ruff format/check, mypy, 437 tests, wheel/sdist build, and diff-check: PASS.
- Local coverage: 90.26%; `uv.lock` byte-identical; no functional change was made.
- No media, SQLite, logs, cookies, or private evidence is tracked.

The final documentation commit/tree and its canonical CI are reconciled in PR #14 after the run
completes, avoiding a self-referential evidence commit.

## Limitations and rollback

Cap 50 and provider exhaustion were not validated. Public capped operation through 20 remains the
last successful evidence. Rollback is documentary; preserve the twenty verified artifacts and do
not repair the failed run outside a new mandate. No merge, tag, release, PyPI, Telegram, WhatsApp,
uncapped operation, second command, or retry occurred.
