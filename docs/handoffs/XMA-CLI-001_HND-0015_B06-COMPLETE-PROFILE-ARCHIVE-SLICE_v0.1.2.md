# HND-0015 — B06 partial final page reconciliation v0.1.2

Status: `B06_OFFLINE_VALIDATED / PUBLIC_ACCEPTANCE_PENDING`

## Baseline

- Governed head: `3e40f53e556ea49a7df29d8a0965f9060c695392`.
- Governed tree: `5d5e465514f5ecc6740acf7eddeb871bd4e20ba2`.
- Base main: `82c28396d442057ef00c48293001f75fb4116861`.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Baseline CI: 40999258984, SUCCESS; 429 tests; 90.54% coverage.

## Defect and regression

Before this rework, a natural provider exhaustion raised after persisted candidates escaped without
a summary. ArchiveService could then complete using the prior total/checkpoint. The deterministic
regression models 20 verified artifacts, a three-candidate final page, then typed exhaustion; it
would leave the run at 20 before the correction and now finishes coherently at 23.

## Typed solution and matrix

DownloadSummary now carries `provider_exhausted`. Only ALL captures the typed
`ProviderExhaustedError` and returns confirmed partial counts; download and BOUNDED still fail when
their requested target is incomplete. ArchiveService re-verifies catalog/filesystem state before
one atomic run/checkpoint write.

| Scenario | Final total | Failed | Page | Terminal |
|---|---:|---:|---:|---|
| 20 → exhaustion | 20 | 0 | 0 | `COMPLETED / PROVIDER_EXHAUSTED` |
| 20 → 1 valid → exhaustion | 21 | 0 | 1 | `COMPLETED / PROVIDER_EXHAUSTED` |
| 20 → 3 valid → exhaustion | 23 | 0 | 1 | `COMPLETED / PROVIDER_EXHAUSTED` |
| 20 → 1 failed + 2 valid → exhaustion | 22 | 1 | 1 | `COMPLETED / PROVIDER_EXHAUSTED` |

Repository mismatch becomes `FAILED / REPOSITORY_INCONSISTENT`. A synthetic checkpoint-write
failure proves the prior total/page/checkpoint remain 20/0/20 and the run becomes sanitized FAILED.

## Files and validation

Changes are limited to download/archive domain and services, offline tests, and B06 governance
documentation. Authentication, gallery-dl, HTTP download behavior, dependencies, workflow, schema,
and published v0.1.2 behavior are unchanged.

- `uv sync --locked --all-groups`: PASS.
- Ruff format/check: PASS.
- mypy: PASS.
- Full suite: 437 PASS; local coverage 90.26%.
- wheel/sdist build: PASS.
- `git diff --check`: PASS.
- `uv.lock`: byte-identical.
- Tracked evidence review: no media, SQLite, logs, cookies, secrets, or private evidence.

The immutable final commit/tree and canonical CI run on that same PR head are recorded in PR #14
after CI completes, avoiding a self-referential evidence-only commit. That final run—not baseline
CI—is the canonical acceptance evidence for this handoff.

## Limitations and rollback

No public acceptance or real provider exhaustion was executed. Roll back the single PRM-0047 commit
to restore the prior boundary; preserve verified artifacts and restore a pre-change catalog backup
when operating on copied evidence. PR #14 stays draft. No X, Firefox, cookies, external disk,
merge, tag, release, PyPI, Telegram, or WhatsApp work occurred.
