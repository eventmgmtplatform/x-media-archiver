# ADR-0007: durable complete-profile archive

Status: Implemented offline; public acceptance pending.

## Decision

`xma archive` has explicit `BOUNDED` and `ALL` modes. `ALL` uses `RESCAN_DEDUP_V2`: verified
target-scoped identities are rebuilt from SQLite and the filesystem, completed artifacts are never
overwritten, every successful page is checkpointed after persistence, and resumption requires a
compatible paused ALL run. No remote cursor is invented.

An ALL run is `COMPLETED` only after the adapter translates the real natural provider terminal to
the typed `ProviderExhaustedError` domain signal. Error text is never inspected to infer
exhaustion. Safety cap, runtime,
free-space, interruption, timeout, or rate limit produce `PAUSED`; local inconsistency or contract
failure produces `FAILED`. A finished command must not leave `RUNNING` without an active writer.

ALL status exposes `goal=PROVIDER_EXHAUSTION`, a null numeric target/remaining value, and an
optional operational cap. Completion requires both `COMPLETED` and `PROVIDER_EXHAUSTED`.
Repository verification precedes cap handling: a cap below verified progress fails without run
mutation, while an equal cap pauses offline as `SAFETY_CAP_REACHED`.

Unexpected application failures are durably classified as `FAILED / UNEXPECTED_FAILURE`; the
original exception remains only as the internal cause and the CLI exposes a constant sanitized XMA
error.

Natural exhaustion may arrive after a partial final page. In ALL mode, DownloadService returns the
confirmed partial result with `provider_exhausted=true`; ArchiveService re-verifies the target-scoped
repository before atomically persisting the new total, failures, page/checkpoint, and terminal
reason. A page advances once only when it added valid artifacts. Persistence or verification failure
preserves the prior checkpoint and fails closed instead of declaring completion.

SQLite schema v3 adds mode, completion reason, failed count, safety settings, and resume timestamp
while transactionally preserving v1/v2 catalogs. `status` remains offline and read-only.

## Consequences

Rescan/dedup is durable but may be inefficient for large profiles. This development cut is tested
only with synthetic fixtures. The boundary-hardening rework is offline validated; public 20→50
acceptance and full-account exhaustion remain pending.
No external data volume, Firefox session, cookie, or public media was used for this decision.

Rollback is a code rollback plus restoration of a pre-migration catalog backup; media artifacts
are never deleted automatically.
