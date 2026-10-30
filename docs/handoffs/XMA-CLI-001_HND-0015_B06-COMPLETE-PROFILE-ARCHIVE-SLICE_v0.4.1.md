# HND-0015 — B06 archive ALL flag propagation rework v0.4.1

Status: `B06_OFFLINE_REWORK_VALIDATED / PUBLIC_RETRY_PENDING`

## Baseline and authorization

- PRM-0051 authorized one exclusively offline correction; no public retry.
- Baseline head/tree: `290f8d617fdb31f98c59358116b133f2962ac83a` /
  `85f03abcac8937d545939edb164ce0fde3d1b979`.
- Baseline CI: 41004515802, SUCCESS; 437 tests; 90.59% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.

## Defect, red regression, and minimal change

The PRM-0050 page target 25 entered DownloadService with `archive_all=True`, but
`manifest_request` was reconstructed with the default false value and failed the interactive 1–20
validation before discovery. A second boundary rejected resumption because the durable run was
`FAILED / DomainError` rather than PAUSED.

Two focused tests were added first and both failed on the baseline. The implementation then:

1. propagates `request.archive_all` explicitly into the reconstructed manifest request; and
2. permits resume only for a compatible ALL run whose terminal state is the known
   `FAILED / DomainError / CompletionReason.FAILED` boundary, converting it to the normal durable
   resume path. Other FAILED classifications remain rejected.

No numeric inference, global bypass, schema, dependency, workflow, authentication, provider,
downloader, or version change was introduced.

## Offline matrices

- Flag propagation: false remains false; true remains true through page and manifest reconstruction.
- ALL absolute totals: 20→25, 25→30, 45→50 and the complete sequence
  20→25→30→35→40→45→50 pass.
- Synthetic failed run: starts total 20/page 4/checkpoint 4 and ends
  `PAUSED / SAFETY_CAP_REACHED`, total 50/page 10/checkpoint 10, never RUNNING.
- Interactive download: limits/additions 1 and 20 remain accepted; 21 remains rejected before
  discovery or persistence. BOUNDED receives no ALL privilege.
- Provider exhaustion, partial final pages, safety cap, SINGLE_POST, profile download, status,
  migrations, lock cleanup, and B02–B06 regressions pass.

## Files and validation

Functional files: `src/xma/application/download.py`, `src/xma/application/archive.py`.
Tests: `tests/application/test_download_service.py`,
`tests/application/test_archive_service.py`. Remaining changes are B06 documentation.

- Locked sync, Ruff format/check, mypy, full pytest, wheel/sdist build, and diff-check: PASS.
- Full suite: 439 PASS; local coverage 90.28%.
- `uv.lock`: byte-identical; dependencies/schema/workflows unchanged.
- No private, media, SQLite, cookie, log, or public evidence is tracked.

The immutable final commit/tree and canonical CI are reconciled in PR #14 after the final run,
avoiding a self-referential evidence commit.

## Limitations and rollback

The real retained repository of twenty artifacts was not read or modified, and PRM-0050 was not
retried. Cap 50/provider exhaustion remain publicly unvalidated until PRM-0052. Rollback the single
PRM-0051 commit to restore the prior behavior; do not alter retained public evidence. No X,
Firefox, cookies, merge, tag, release, PyPI, Telegram, or WhatsApp activity occurred.
