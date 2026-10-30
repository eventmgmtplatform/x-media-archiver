# XMA-CLI-001-PRM-0047 — B06 partial final page reconciliation v0.1.0

Status: `HUMAN_AUTHORIZED / EXECUTED_ONCE`

## Baseline and boundary

Leonel authorized one exclusively offline rework on draft PR #14 from head
`3e40f53e556ea49a7df29d8a0965f9060c695392`, tree
`5d5e465514f5ecc6740acf7eddeb871bd4e20ba2`, with main at
`82c28396d442057ef00c48293001f75fb4116861`. X, Firefox, cookies, real profiles,
public downloads, external storage, merge, tags, releases, PyPI, Telegram, and WhatsApp were
prohibited.

## Required behavior

For `archive --all`, natural typed provider exhaustion after valid candidates must return a typed
partial download result. ArchiveService must verify target-scoped catalog/filesystem state, persist
confirmed totals and failures, advance the page exactly once only when valid progress occurred,
atomically update checkpoint/run, and then complete as `PROVIDER_EXHAUSTED`.

Zero-progress exhaustion completes without advancing the page. BOUNDED/download behavior must not
convert incomplete work into success. Provider text must never infer exhaustion. Repository
inconsistency, regression behind checkpoint, or checkpoint persistence failure must fail closed,
retain valid artifacts, preserve the prior checkpoint, and expose only sanitized classifications.

## Acceptance

Offline tests cover 20→20, 20→21, 20→23, failed candidates, atomic checkpoint failure,
repository mismatch, restart/status, transients, bounded behavior, and B02–B06 regressions. Locked
sync, Ruff, mypy, full pytest with at least 90% coverage, build, and diff-check must pass. Publish
HND-0015 v0.1.2, leave PR #14 draft, and stop at
`B06_OFFLINE_VALIDATED / PUBLIC_ACCEPTANCE_PENDING`.
