# HND-0015 — B06 public cap and resume acceptance v0.2.0

Status: `B06_PUBLIC_CAP_RESUME_VALIDATED / FULL_ACCOUNT_PENDING`

## Authorization and baseline

- Authorization: PRM-0048, one capped public sequence only.
- Baseline head: `f71fe4eeef57db3a5d48eaaafbce197127da2ba2`.
- Baseline tree: `ac1f38e1441922e48d4c47aa6f7639048b91615f`.
- Base main: `82c28396d442057ef00c48293001f75fb4116861`.
- Baseline CI: 41000564192, SUCCESS; 437 tests; 90.59% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.

The public target, Firefox selector, user paths, cookies, headers, tokens, media URLs, and raw logs
remain local and are represented only as `<LOCAL_TARGET>`, `<LOCAL_PROFILE>`, and
`<LOCAL_B06_REPOSITORY>`.

## Acceptance matrix

| Phase | Code | Duration | Before | After | Page/checkpoint | Result |
|---|---:|---:|---:|---:|---:|---|
| `--all --max-items 5` | 0 | 7 s | 0 | 5 | 1 / 1 | `PAUSED / SAFETY_CAP_REACHED` |
| `--all --resume --max-items 10` | 0 | 7 s | 5 | 10 | 2 / 2 | `PAUSED / SAFETY_CAP_REACHED` |

Both phases used the same durable run. Each reported `goal=PROVIDER_EXHAUSTION`, `complete=false`,
and `resumable=true`; the operational caps were 5 and 10. Offline status reproduced the same
state and did not change timestamps.

## Integrity and retained evidence

- Final media/sidecars/artifacts/completed jobs/distinct identities: 10/10/10/10/10.
- SQLite `PRAGMA integrity_check`: `ok`.
- Hash, size, sidecar, manifest, catalog, and filesystem reconciliation: PASS.
- Original five media hashes remained unchanged after resumption; no overwrite occurred.
- Aggregate phase-1 hash set: `39c28b2aed14a0fc60494226c21ce83409716a8ee3300f54cff450b6a0b5c2f6`.
- Aggregate final hash set: `93b688e550241c0ac9da5ca60c6f8341f4c6306f7ce064716f3ebe8a21922d77`.
- Final retained repository size: 48,302,350 bytes.
- Available space: 23,780,864,000 bytes before phase 1; 23,748,661,248 after phase 1;
  23,747,948,544 before phase 2; 23,723,892,736 after phase 2.
- Zero `.part` and `.tmp`; archive lock released.
- The exact repository is retained under `<LOCAL_B06_REPOSITORY>` for Leonel/Chat review.

## Validation and canonical CI

- Locked sync, Ruff format/check, mypy, full pytest, wheel/sdist build, and diff-check: PASS.
- Full suite: 437 PASS; local coverage 90.26%.
- `uv.lock`: byte-identical; no functional changes occurred during or after acceptance.
- Tracked-file review: no media, SQLite, raw logs, cookies, or private evidence.

The immutable final documentation commit/tree and its canonical green CI are reconciled in PR #14
after that run completes, avoiding a self-referential evidence-only commit. That run is the final CI
evidence for this handoff.

## Limitations and rollback

This evidence validates only safety caps, incremental persistence, deduplication, resumption 5→10,
artifact preservation, and durable status. It does not validate provider exhaustion, full-account
archive, an uncapped run, mass operation, or totals above ten. No retry or inspect occurred.

Rollback is documentary for this acceptance: preserve the retained repository, do not delete or
overwrite verified artifacts, and return to the prior PR head if the evidence is rejected. PR #14
remains draft; merge, tag, release, PyPI, Telegram, WhatsApp, and other platforms remain prohibited.
