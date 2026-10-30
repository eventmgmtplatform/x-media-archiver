# HND-0015 — B06 public resume 10→20 v0.3.0

Status: `B06_PUBLIC_LIMIT_20_VALIDATED / FULL_ACCOUNT_PENDING`

## Authorization and baseline

- Authorization: PRM-0049, one public resume of the retained durable run.
- Baseline head/tree: `6d364d92f0cde95118c1458af5d4df2073453952` /
  `cc8bf84bc373af12f3948de170ff37174ecb2f68`.
- Base main: `82c28396d442057ef00c48293001f75fb4116861`.
- Baseline CI: 41001882660, SUCCESS; 437 tests; 90.59% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.

Target, profile, account, local paths, cookies, tokens, headers, URLs, query strings, and raw logs
remain private. They are represented only as `<LOCAL_TARGET>`, `<LOCAL_PROFILE>`, and
`<LOCAL_B06_REPOSITORY>`.

## Public matrix 10→20

- Command count: one; retry count: zero; inspect count: zero.
- Exit code/duration: 0 / 21 seconds.
- Same durable run as PRM-0048; verified initial/final total: 10→20.
- New/total media, sidecars, artifacts, completed jobs, identities: 10/20 each final category.
- Terminal: `PAUSED / SAFETY_CAP_REACHED`.
- `goal=PROVIDER_EXHAUSTION`, `operational_cap=20`, `complete=false`, `resumable=true`.
- Page/checkpoint: 4/4; failed total: 0.
- Sanitized discovery telemetry: 2 workers, 2 auth loads, 2 extractor starts, 2 profiles,
  35 video observations, 25 duplicates skipped, and 8 candidate messages.

## Integrity and retained evidence

- SQLite integrity: `ok`; catalog/filesystem, hashes, sizes, sidecars, and manifest: PASS.
- All ten initial hashes remained identical; no artifact was overwritten.
- Initial aggregate hash set:
  `93b688e550241c0ac9da5ca60c6f8341f4c6306f7ce064716f3ebe8a21922d77`.
- Final aggregate hash set:
  `583dd44193c2d2fec37470a0cfcec9ddeba0989d9e25a6e199a3b594c8f61168`.
- Final retained repository size: 92,022,593 bytes.
- Available space: 23,699,136,512 bytes before; 23,654,858,752 bytes after.
- Zero `.part`/`.tmp`; lock released; offline status reproduced state without timestamp mutation.
- The exact twenty-artifact repository remains retained as `<LOCAL_B06_REPOSITORY>`.

## Validation and canonical CI

- Locked sync, Ruff format/check, mypy, full pytest, wheel/sdist build, and diff-check: PASS.
- Full suite: 437 PASS; local coverage 90.26%.
- `uv.lock`: byte-identical; no functional changes occurred during or after acceptance.
- No media, SQLite, raw logs, cookies, or private evidence is tracked.

The final documentation commit/tree and canonical green CI are reconciled in PR #14 after that run
completes, avoiding a self-referential evidence commit. That run is the final CI evidence for this
handoff.

## Limitations and rollback

The provider did not exhaust before cap 20. This validates capped durable operation through twenty,
not a complete account, uncapped run, mass archive, or any total above twenty. Rollback is
documentary: retain all verified artifacts and return to the prior PR head if Chat rejects the
evidence. No retry, alternate target/profile, merge, tag, release, PyPI, Telegram, or WhatsApp was
performed.
