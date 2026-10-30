# XMA-CLI-001-PRM-0045 — B06 complete-profile archive slice v0.1.0

State: HUMAN AUTHORIZED; offline implementation only under Addendum 01.

Baseline: `main` at `82c28396d442057ef00c48293001f75fb4116861`, tree
`c2c3da45f3d5525cd8dadb3c57b8bd0847456fb0`.

Implement `xma archive @HANDLE --all` with durable resume, target-scoped deduplication,
incremental persistence, consistent checkpoints, configurable batches/rate limiting, explicit
provider exhaustion, safe interruption, offline status, and v0.1.2 compatibility. Preserve bounded
archive and `download` behavior. Do not invent a remote cursor.

Completion is permitted only for explicit provider exhaustion. Safety cap, runtime, disk pressure,
timeout, rate limit, and interruption pause; repository or contract inconsistency fails. No command
may finish leaving an active `RUNNING` state without a writer.

Addendum 01 cancels OPS-0002 and removes the external volume and PRM-0040 evidence as
preconditions. This execution is fully synthetic/offline: no X, Firefox, cookies, real media, or
public acceptance. Final state is `B06_OFFLINE_READY / PUBLIC_ACCEPTANCE_PENDING`; no merge, tag,
release, PyPI, Telegram, or WhatsApp.
