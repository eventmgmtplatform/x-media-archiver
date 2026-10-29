# XMA-CLI-001-PRM-0032 — v0.1.1 download recovery, additive mode and provider-best quality

**Version:** 0.1.0
**State:** HUMAN AUTHORIZED
**Addendum:** 001 — DOWNLOAD LIMIT 1–10 AND DURABLE-ARCHIVE ROUTING

## Authority and baseline

Leonel authorized one bounded hotfix from `origin/main`
`4ffa3d86a68acc00bb6d729ddf53766959abd6a3`, with published `v0.1.0` target
`c997cce488b4486ffd8dc079cd25819bec402b77`, on branch
`hotfix/v0.1.1-download-recovery-quality` and a draft PR to main.

## Required corrections

1. Reconcile `FAILED_FINAL` jobs without artifacts when no final/staging/sidecar residue exists;
   preserve audit and increment attempts on an explicit retry. Every completed/artifact mismatch
   remains fail-closed.
2. Treat absolute limits at or below verified existing totals as successful offline no-ops.
3. Add mutually exclusive `--add`; no explicit mode preserves legacy absolute limit 1.
4. Bound discovery using `--max-scan 1..500` (default 100), at most two workers and timeouts.
5. Accept only `--quality best`, explicitly enable gallery-dl Twitter videos, and persist sanitized
   `quality_policy=provider-best` plus safe observed media fields, never media URLs.
6. Clean `.part`, temporary sidecars and empty media-index directories after failure.

## Addendum 001 — governing range

This addendum supersedes any earlier statement limiting interactive download to five. `--limit`
accepts every integer 1–10 as the absolute verified total. `--add` accepts 1–10 and computes
`target_total = existing_verified_total + requested_additional`. A result above ten is rejected
before provider construction, authentication, discovery, HTTP or catalog mutation with exit 2 and
guidance to the durable `xma archive` workflow. Existing totals above an absolute request are
preserved; artifacts are never deleted to reduce a repository.

The global v0.1.1 maximum, including archive, remains ten. This mandate does not authorize mass
download, scheduler support, merge, tag, Release, PyPI, dot or public limit-ten acceptance.

## Validation and acceptance

Offline fixtures must cover all limit/add values, invalid preflight, retry, cleanup, exhaustion,
fresh-URL recovery, quality metadata, SINGLE_POST and archive/status regressions. Run locked sync,
Ruff, mypy, full pytest with coverage >=90%, build and diff checks before network and require green
CI on the functional commit.

Only after that gate, execute exactly four authenticated public commands on one new repository:
`--add 1` (0→1), `--add 1` (1→2), `--add 3` (2→5), and `--limit 1` as an offline no-op retaining
five. Use quality best, max-scan 100, two 30-second workers and an external 120-second timeout. Stop
at the first failure; do not retry or test public exhaustion.
