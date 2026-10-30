# HND-0015 — B06 full-account E2E best-quality acceptance v0.6.0

Status: `REWORK_REQUIRED`

## Authorization and baseline

- PRM-0053 authorized exactly one new-repository ALL execution against
  `<LOCAL_E2E_TARGET>`, provider-best quality, and an operational cap of 30.
- Baseline head/tree: `ff178d3e9e686a357eace746823f1f318ceb1bee` /
  `f2a086d761092e2388ac146eff243cb902baf291`.
- Baseline CI: [41023223447](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41023223447),
  SUCCESS; 439 tests; 90.61% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- The final documentation commit/tree and its canonical CI are reconciled in PR #14 after the
  commit to avoid self-referential evidence.

## Preconditions

The new `<LOCAL_E2E_REPOSITORY>` was created empty under the local home filesystem and was not the
retained cap-50 repository. The contained Firefox boundary reported a complete session without
exporting or logging cookie values. Available space was 23,456,747,520 bytes, above the 15 GiB
entry threshold and 5 GiB reserve. Git baseline, draft PR, CI, clean worktree, unchanged `uv.lock`,
and forbidden-file scan all passed.

The retained cap-50 repository was fingerprinted before the operation. Afterward its 50-video
aggregate remained `090b49f30d9822f7039f3c55baa86d7f07d5df5013caba74e07f0035f3857fb1`
and its catalog hash remained
`53d8157e85b06931b4229791c12892f68ef8a616dfd5eec1401727a81fa37ee6`.

## Single public execution

Exactly one non-resume `archive --all` command ran with batch 5, cap 30, provider-best quality,
the governed timeouts, `<LOCAL_PROFILE>`, and `<LOCAL_E2E_TARGET>`. It completed with code 0 in
398 seconds. No inspect, retry, second archive, alternate target/profile, or external disk was used.

The durable run produced:

- 22 videos, 22 sidecars, 22 artifacts, 22 COMPLETED jobs, and 22 distinct identities;
- `COMPLETED / PROVIDER_EXHAUSTED`, `goal=PROVIDER_EXHAUSTION`, complete true and resumable false;
- page/checkpoint 5/5, failed total 0, and operational cap 30;
- SQLite `integrity_check=ok`, all sizes/hashes coherent, lock released, zero `.part`/`.tmp`;
- provider-best quality;
- final aggregate `14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`;
- retained size 6,401,973,208 bytes and 16,974,577,664 bytes free afterward.

The total 22 is within the expected 20–23 range, and the typed provider-exhaustion terminal is
genuine. However, the last-page manifest records `exhausted=true`, requested total 25, actual total
22, and `complete=false`. PRM-0053 explicitly requires a complete manifest. The durable run and
repository are internally consistent, but this cross-evidence mismatch prevents declaration of
`B06_FULL_ACCOUNT_E2E_VALIDATED / PUBLIC_ACCEPTANCE_COMPLETE` and is classified
`REWORK_REQUIRED`. No functional correction was authorized or attempted.

## Validation

Both pre- and post-execution matrices passed:

- `uv sync --locked --all-groups`: PASS;
- Ruff format/check: PASS;
- mypy: PASS;
- pytest: 439 PASS, local coverage 90.28%;
- wheel/sdist build: PASS;
- `git diff --check`: PASS;
- `uv.lock`: byte-identical;
- no private data, media, SQLite, cookie, or raw log is tracked.

Raw logs were retained only until sanitized evidence and PR reconciliation were complete, then
removed. `<LOCAL_E2E_REPOSITORY>` remains intact under HOME.

## Limitation and rollback

The required follow-up is an offline, governed reconciliation of final-page manifest semantics:
typed provider exhaustion must be represented consistently without weakening bounded-download
completeness. Do not repeat this public command to diagnose it. Rollback is the prior documentation
commit only; preserve both local evidence repositories and do not delete or rewrite artifacts.
