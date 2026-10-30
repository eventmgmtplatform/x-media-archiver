# ADR-0007: durable complete-profile archive

Status: Implemented offline; public acceptance pending.

## Decision

`xma archive` has explicit `BOUNDED` and `ALL` modes. `ALL` uses `RESCAN_DEDUP_V2`: verified
target-scoped identities are rebuilt from SQLite and the filesystem, completed artifacts are never
overwritten, every successful page is checkpointed after persistence, and resumption requires a
compatible paused ALL run. No remote cursor is invented.

An ALL run is `COMPLETED` only after an explicit natural provider terminal. Safety cap, runtime,
free-space, interruption, timeout, or rate limit produce `PAUSED`; local inconsistency or contract
failure produces `FAILED`. A finished command must not leave `RUNNING` without an active writer.

SQLite schema v3 adds mode, completion reason, failed count, safety settings, and resume timestamp
while transactionally preserving v1/v2 catalogs. `status` remains offline and read-only.

## Consequences

Rescan/dedup is durable but may be inefficient for large profiles. This development cut is tested
only with synthetic fixtures. Public 20→50 acceptance and full-account exhaustion remain pending.
No external data volume, Firefox session, cookie, or public media was used for this decision.

Rollback is a code rollback plus restoration of a pre-migration catalog backup; media artifacts
are never deleted automatically.
