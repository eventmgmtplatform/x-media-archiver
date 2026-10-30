# HND-0015 — B06 evidence reconciliation and certification v0.7.0

Status: `B06_FULL_ACCOUNT_E2E_VALIDATED / PUBLIC_ACCEPTANCE_COMPLETE / READY_FOR_MERGE_REVIEW`

## Authorization and baseline

- PRM-0055 authorized offline verification, atomic reconciliation of only the retained manifest's
  `complete` field, certification, and documentation.
- Baseline head/tree: `781d71a640217c62120ee09947446799fb6908f6` /
  `01984a3d4135b3526c0cb273b3dc6f4f90aea9d8`.
- Baseline CI: [41026481902](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41026481902),
  SUCCESS; 442 tests; 90.61% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Final documentary commit/tree and canonical CI are reconciled in PR #14 after the commit.

No X, Firefox, cookies, provider, archive, download, sync, inspect, or Pages deployment was used.

## Evidence and atomic reconciliation

Before modification, one offline status call was read-only and the repository matched every
precondition: 22 videos/sidecars/artifacts/COMPLETED jobs/identities; provider-best; durable
`COMPLETED / PROVIDER_EXHAUSTED`; goal `PROVIDER_EXHAUSTION`; page/checkpoint 5/5; failed total 0;
integrity `ok`; no residues; lock free; aggregate
`14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.
The separate cap-50 repository also retained its prior media and catalog fingerprints.

The original manifest was copied alone to `<LOCAL_EVIDENCE_DIR>` and retained for Chat review.
Its hash was `50eb3de528146dac46896f66632723995caa8a7b71960cf1f24426ddb0be2324`.
An in-memory JSON copy changed only `complete:false→true`, preserved `exhausted=true`, permissions
and every other logical field, then used same-directory temporary creation, file `fsync`,
`os.replace`, directory `fsync`, and residual cleanup. The repaired hash is
`298f186eb526518ccee06a48a36e9a62c02311debc5e24b4d2b246a15c9c28af`.

Post-repair logical comparison proved `complete` was the sole difference. Catalog hash
`d27c781dba39f7dc7b4cec270ab6cd66493e9b19e0c69653ab91db2d0bae93d2`, media aggregate,
sidecars, sizes, run/checkpoint timestamps and state remained unchanged. The single posterior
status call remained read-only and reported the same typed completed state.

## Decision and validation

CERT-0001 records `VALIDATED_WITH_OBSERVATIONS`. B06 now satisfies its public acceptance criteria
for the observed account and is ready for merge review, but this handoff does not authorize merge.

- Locked sync, Ruff format/check, mypy, pytest, wheel/sdist build, and diff-check: PASS.
- Suite: at least 442 tests; local coverage ≥90%.
- `uv.lock`, source, schema, migrations, dependencies, workflows and version: unchanged.
- No local evidence, media, SQLite, cookies, secrets or raw logs are tracked.
- `docs/wiki` is prepared for automatic Pages publication only after an authorized merge to main;
  `.github/workflows/pages.yml` is unchanged and no manual Pages execution occurred.

## Limitations and rollback

`RESCAN_DEDUP_V2` may be inefficient at scale; only one public account is certified; Firefox local
session authentication remains an external dependency; thousands of downloads, scheduler and mass
operation are not certified. PRM-0056 reporting, Telegram and WhatsApp remain backlog.

Rollback restores the preserved original manifest by the same atomic procedure after hash
verification. Do not modify artifacts or catalog state. No merge, tag, Release or PyPI occurred.
