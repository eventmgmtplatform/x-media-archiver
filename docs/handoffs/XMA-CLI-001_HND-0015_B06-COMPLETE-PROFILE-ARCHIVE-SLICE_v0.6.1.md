# HND-0015 — B06 manifest exhaustion semantics v0.6.1

Status: `B06_MANIFEST_SEMANTICS_OFFLINE_VALIDATED / EVIDENCE_REPAIR_PENDING`

## Authorization and baseline

- PRM-0054 authorized an exclusively offline correction of final-manifest semantics.
- Baseline head/tree: `2b8c96c017e3ad3d83e42720db1503f374806c5c` /
  `f0b5a4b6754eb4ab60153787752426dcb9a17e03`.
- Baseline CI: [41025642089](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41025642089),
  SUCCESS; 439 tests; 90.61% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- The final commit/tree and canonical CI are reconciled in PR #14 after the final documentation
  commit, avoiding self-referential evidence.

No X, Firefox, cookies, real profile, download, inspect, or retained multimedia repository was read
or modified.

## Preserved public evidence

PRM-0053 remains immutable evidence: code 0; 22 intact provider-best assets; durable
`COMPLETED / PROVIDER_EXHAUSTED`; goal `PROVIDER_EXHAUSTION`; page/checkpoint 5/5; zero failures;
integrity `ok`; zero residues; aggregate
`14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.
Its retained manifest was not opened or repaired during this mandate.

## Reproduced defect and correction

The focused regression constructed an entirely synthetic ALL page with requested total 25, 22
valid identities, zero failures, and a typed `ProviderExhaustedError`. Before the change it failed
exactly at `manifest["complete"]`: `exhausted=true` but `complete=false`.

The minimal change replaces the broad inference
`not complete and not isinstance(last_error, DownloadError)` with explicit state:

- `requested_total_reached = total_after >= requested_total`;
- `provider_exhausted = true` only after typed `ProviderExhaustedError`;
- manifest complete when the requested total is reached, or when ALL has genuine typed exhaustion
  and zero failed downloads;
- manifest exhausted exactly when typed provider exhaustion occurred;
- `DownloadSummary.complete` retains requested-total semantics so ArchiveService continues to own
  durable ALL completion through `provider_exhausted`.

No count is hardcoded. No behavior outside the final manifest decision was changed.

## Offline matrix

- ALL typed exhaustion: 22/25, 20/25, and 0/5 produce manifest
  `complete=true / exhausted=true`; summary retains `provider_exhausted=true`.
- ALL total reached: 25/25 produces `complete=true / exhausted=false` without a typed terminal.
- Timeout and generic incompleteness: `complete=false / exhausted=false`.
- DownloadError followed by incomplete discovery: no full-account completion and no inferred
  exhaustion.
- BOUNDED early typed exhaustion continues to fail closed and does not gain ALL completion.
- Existing ArchiveService coverage preserves partial-final-page checkpointing, safety-cap pauses,
  transient/worker failure handling, and durable `COMPLETED / PROVIDER_EXHAUSTED` only for the typed
  ALL terminal.
- Interactive limit/add 1–20, SINGLE_POST, migrations, status, and B02–B06 regressions remain green.

The principal test was red before the fix and green afterward. Full validation: 442 tests PASS,
local coverage 90.28%; locked sync, Ruff format/check, mypy, wheel/sdist build, and diff-check PASS.
`uv.lock`, dependencies, schema, workflows, and project version are unchanged. No private, media,
SQLite, cookie, or log evidence is tracked.

## Files, limitations, and rollback

Functional file: `src/xma/application/download.py`. Regression file:
`tests/application/test_download_service.py`. Remaining files are B06 documentation.

This offline correction does not retroactively repair or certify the retained PRM-0053 manifest.
`FULL_ACCOUNT_E2E_VALIDATED`, `PUBLIC_ACCEPTANCE_COMPLETE`, and B06 closure are not declared.
PRM-0055 is required for any governed reconciliation of retained evidence. Roll back the functional
commit to restore the prior manifest behavior; do not alter either retained multimedia repository.
