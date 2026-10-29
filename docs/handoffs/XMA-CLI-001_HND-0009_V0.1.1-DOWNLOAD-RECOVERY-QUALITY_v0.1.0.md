# XMA-CLI-001 — HND-0009 v0.1.0 download recovery and quality

**State:** IMPLEMENTED / OFFLINE_VALIDATED / CI_PENDING / PUBLIC_ACCEPTANCE_PENDING

## Baseline

- `origin/main`: `4ffa3d86a68acc00bb6d729ddf53766959abd6a3`.
- published `v0.1.0` target: `c997cce488b4486ffd8dc079cd25819bec402b77`.
- branch: `hotfix/v0.1.1-download-recovery-quality`.
- authority: PRM-0032 v0.1.0 plus Addendum 001 v0.1.1.

## Defects and decisions

The exact failed database shape (completed discovery, one media asset, `FAILED_FINAL` job with one
attempt, zero artifacts and no files) previously failed reconciliation. It now remains auditable and
can transition explicitly to a second queued/downloading attempt. Only completed jobs require an
artifact; unexpected final/staging/sidecar files, artifact without completed job, and completed job
without artifact remain conflicts.

Lower absolute totals are offline no-ops. Additive mode computes from the verified target-scoped
repository total. Both modes accept 1–10, remain mutually exclusive and fail before network when
the result would exceed ten. Discovery is bounded by max-scan, worker count and timeout.

`best` maps to the provider's best direct variant and persists only `provider-best`, dimensions,
MIME, extension, size and hash. A second bounded worker may refresh the ephemeral URL after one
media failure; no URL is persisted.

## Evidence to reconcile after final CI and acceptance

- Final SHA/tree and changed-file inventory: recorded in the draft PR after the last commit.
- Offline suite, coverage, Ruff, mypy, build and `uv.lock` evidence: recorded after final validation.
- Public matrix: 0→1, 1→2, 2→5 and lower-limit offline no-op, or the first sanitized blocker.
- CI URL and final state: recorded in the PR body to avoid an evidence-only commit cycle.

No local path, Firefox selector, cookie, signed URL, media, SQLite or raw log may be published.
Rollback is a revert of the hotfix commit; completed repositories are never rewritten.
