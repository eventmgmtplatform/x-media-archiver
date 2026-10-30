# HND-0015 — B06 terminal ALL idempotency v0.7.1

Status: `B06_COMPLETED_NOOP_OFFLINE_VALIDATED / PUBLIC_NOOP_TEST_PENDING`

## Authorization and baseline

- PRM-0057 authorized one exclusively offline rework of terminal `archive --all` idempotency.
- Baseline head/tree: `37b3cbd88c659f6fa5705986c0a4b12c44ff8a7d` /
  `1a9b19d7cc967ea59b598e1164131345ce1aa13d`.
- Baseline CI: [41027287076](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41027287076),
  SUCCESS; 442 tests; 90.61% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Functional commit/tree: `e79c7eab3bf85a00d47b69fcc9661b66e4660d04` /
  `52d748d1ab0fb32444d2ec0e7bba9cb2ea8dd395`.
- Final documentary commit/tree and canonical CI are reconciled in PR #14 after this handoff is
  committed, avoiding a self-referential evidence commit.

No X, Firefox, cookies, provider, public archive/download, retained evidence repository, merge,
tag, Release or PyPI operation was used. CERT-0001 v0.1.0 and all public evidence were unchanged.

## Defect, reproduction and correction

Before the correction, `_prepare_all_run` rejected a completed ALL run when `--resume` was used
and discarded it without `--resume`. The red regression consequently entered the page loop instead
of returning the certified terminal run; it was interrupted after reproducing that behavior.

The narrow correction preserves a compatible completed ALL run through preparation. After the
repository lock is acquired and the verified target total is read, `ArchiveService` returns the
existing run before any `replace`, `store.put`, provider or download operation only when all of
these are true: mode ALL, status COMPLETED, reason PROVIDER_EXHAUSTED, failed total zero, matching
target and `verified_total == downloaded_total`. A supplied `max_items` below verified progress is
still rejected. No numeric total is used to infer terminal privilege.

## Offline regression matrix

| Case | Result |
| --- | --- |
| Same target, without `--resume` | Same durable run returned; PASS |
| Same target, with `--resume` | Same run; timestamps and `resumed_at` unchanged; PASS |
| Two consecutive invocations | Same run twice; zero writes; PASS |
| Repository verification | Exact total queried before return; PASS |
| Checkpoint ahead/behind repository | Sanitized fail-closed; PASS |
| Repository integrity failure | Fail-closed before provider/download; PASS |
| Target mismatch | Fail-closed before verification/provider/download; PASS |
| `max_items` below verified total | Sanitized `DomainError`; PASS |
| Other completion reason | No terminal privilege; PASS |
| PROVIDER_EXHAUSTED with failures | No terminal privilege; PASS |
| PAUSED/RUNNING/FAILED recovery | Existing regression behavior preserved; PASS |
| Safety cap and BOUNDED | Existing regression behavior preserved; PASS |
| Synthetic manifest | SHA-256 and content unchanged across both no-ops; PASS |

The counting store observed zero `put` calls for successful no-ops. The synthetic download boundary
observed zero `execute_incremental` calls, and the provider boundary was never entered. The existing
run ID, status, reason, totals, page/checkpoint, timestamps, cooldown, historical caps and manifest
remained unchanged.

## Files and validation

Functional files:

- `src/xma/application/archive.py`
- `tests/application/test_archive_service.py`

Evidence file:

- `docs/handoffs/XMA-CLI-001_HND-0015_B06-COMPLETE-PROFILE-ARCHIVE-SLICE_v0.7.1.md`

Local validation:

- `uv sync --locked --all-groups`: PASS.
- `uv run ruff format --check .`: PASS (187 files).
- `uv run ruff check .`: PASS.
- `uv run mypy`: PASS (44 source files).
- `uv run pytest`: PASS, 451 tests, 90.59% total coverage.
- `uv build`: PASS; wheel and sdist built.
- `git diff --check`: PASS.
- `uv.lock`, dependencies, schema, workflows and public CLI: unchanged.
- Tracked-file review: no media, SQLite, private manifests, cookies, secrets or raw logs added.

The final CI run and its exact head/tree are recorded in PR #14 once CI completes on the published
handoff commit.

## Limitations and rollback

The behavior is validated only with deterministic offline repositories and synthetic evidence.
No public no-op repetition was executed; that remains `PUBLIC_NOOP_TEST_PENDING` and requires a
separate authorization. This change does not add refresh semantics to an exhausted account.

Rollback reverts the functional commit and this handoff commit. It requires no catalog migration,
artifact rewrite or evidence repair because schema and persisted data formats did not change.
