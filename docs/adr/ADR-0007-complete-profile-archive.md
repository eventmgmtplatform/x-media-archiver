# ADR-0007: durable complete-profile archive

Status: Manifest semantics corrected offline; retained-evidence reconciliation pending.

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

Rescan/dedup is durable but may be inefficient for large profiles. Boundary hardening and failed-run
recovery are covered by deterministic offline fixtures. PRM-0052 publicly validated the capped
20→50 continuation, but full-account exhaustion remains pending. No external data volume was used;
browser secrets and public-media URLs remain local and are not persisted in project evidence.

PRM-0048 publicly validated only the bounded safety controls and durable resumption: a new local
repository advanced 0→5 and then 5→10 on the same run, pausing at each configured cap with intact
artifacts and checkpoints. This does not validate provider exhaustion, a complete account archive,
mass operation, or an uncapped run.

PRM-0049 extended the same durable run from 10→20. It again stopped at the configured safety cap,
with page/checkpoint 4 and all prior hashes preserved. Provider exhaustion was not observed, so
full-account completion remains unvalidated.

PRM-0050 attempted the single authorized resume toward cap 50 but failed locally before discovery:
the archive page target 25 was rebuilt as a non-ALL `DownloadRequest` for manifest handling and was
rejected by the interactive 1–20 contract. The run failed cleanly at 20 with its artifacts and
checkpoint intact. Cap 50 and provider exhaustion therefore remain unvalidated pending rework.

PRM-0051 corrected that boundary offline: every internal DownloadRequest reconstruction now
preserves the explicit `archive_all` authority, while interactive download remains limited to
1–20. Recovery of the known `FAILED / DomainError` ALL run is narrowly permitted and validated
synthetically through absolute pages 25, 30, 35, 40, 45, and 50. Public retry remains pending.

PRM-0052 consumed the single authorized retry on the same retained run. It preserved the original
20 hashes, added 30 verified artifacts, and stopped at total 50 with page/checkpoint 10/10,
`PAUSED / SAFETY_CAP_REACHED`, zero failures, integrity `ok`, and no residues. This validates the
cap-50 recovery path only; typed provider exhaustion and full-account completion remain pending.

PRM-0053 then exercised a new repository and distinct sanitized target. Typed provider exhaustion
occurred at 22 intact provider-best artifacts, with durable status `COMPLETED`, page/checkpoint 5/5,
zero failures, and integrity `ok`. The last download-page manifest simultaneously recorded
`exhausted=true` and `complete=false` because its requested page target was 25 while the provider
ended at 22. That inconsistency is `REWORK_REQUIRED`: full-account acceptance is not declared until
the final manifest represents typed exhaustion consistently. The public command must not be retried.

PRM-0054 corrects the semantics offline. Manifest completeness is now requested-total completion,
or typed provider exhaustion in ALL mode with zero failed downloads; the exhausted bit is driven
only by the typed terminal. Summary requested-total semantics and ArchiveService ownership of
durable ALL completion remain unchanged. Timeout, transient/incomplete discovery, DownloadError,
and BOUNDED mode remain fail-closed. The retained PRM-0053 manifest was not read or repaired, so
evidence reconciliation and B06 acceptance remain pending PRM-0055.

Rollback is a code rollback plus restoration of a pre-migration catalog backup; media artifacts
are never deleted automatically.
