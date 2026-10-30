# B06 `archive --all` development runbook

This runbook describes the unaccepted `0.2.0.dev0` interface. It is not part of the published
v0.1.2 contract and must not be used for public or unattended archival without a later decision.

```bash
uv run xma archive @HANDLE --all --max-items 50 --batch-size 5 \
  --request-interval 2 --max-runtime 3600 --min-free-space-gib 10 \
  --repository ./repository-HANDLE --quality best \
  --auth-browser firefox --auth-profile '<LOCAL_PROFILE>'

uv run xma archive @HANDLE --all --resume --max-items 50 \
  --repository ./repository-HANDLE --quality best \
  --auth-browser firefox --auth-profile '<LOCAL_PROFILE>'

uv run xma status --repository ./repository-HANDLE --json
```

`goal=PROVIDER_EXHAUSTION` identifies unbounded ALL status. Its `requested_total` and `remaining`
fields are null until provider exhaustion is confirmed; `operational_cap` is a safety control, not
the archive goal. `PROVIDER_EXHAUSTED` is the only successful completion reason for ALL and is
accepted only through the typed provider-exhaustion boundary. `SAFETY_CAP_REACHED`,
`MAX_RUNTIME_REACHED`, `LOW_DISK_SPACE`, `INTERRUPTED`, and `PROVIDER_TRANSIENT` are resumable
pauses. `FAILED` requires offline integrity diagnosis. `--resume` fails closed unless a compatible
ALL run is paused. `RESCAN_DEDUP_V2` rescans and deduplicates; it is not a remote cursor.

The repository is verified before an ALL cap is applied. A cap below verified progress is rejected
without discovery or run mutation; an equal cap is an offline `PAUSED / SAFETY_CAP_REACHED`; a
higher cap may continue. Unexpected failures are reported only as the sanitized
`archive failed: unexpected internal failure` contract while the durable run records
`UNEXPECTED_FAILURE`.

The last provider page may contain fewer candidates than the batch size. Confirmed artifacts are
retained, verified against the target-scoped repository, and checkpointed before ALL becomes
`COMPLETED / PROVIDER_EXHAUSTED`. A zero-candidate final page does not increment `page_number`; a
partial page with valid progress increments it once. Any verification or checkpoint failure is a
terminal sanitized failure and must be diagnosed offline before resumption.

Back up the whole repository before migration. Never delete or overwrite verified artifacts.
Public acceptance and complete-account operation remain pending.

The governed PRM-0048 acceptance demonstrated a capped sequence only: `--max-items 5`, followed by
`--resume --max-items 10`, on the same repository and run. Both commands ended
`PAUSED / SAFETY_CAP_REACHED`, remained resumable, and preserved prior hashes. Operators must not
interpret this result as provider exhaustion or authorization for uncapped/full-account archival.

PRM-0049 resumed that exact run from 10→20 and again ended
`PAUSED / SAFETY_CAP_REACHED`. The evidence validates capped durable growth through twenty, but not
the natural provider terminal. Do not continue above twenty or remove the cap without a new human
decision.

Known blocker from PRM-0050: a resume whose next absolute page target exceeds 20 is rejected while
DownloadService reconstructs its manifest request without the ALL-mode exemption. The command ends
`FAILED / DomainError` before discovery and preserves the prior checkpoint. Do not retry or attempt
cap 50 until a separately authorized rework corrects and validates that boundary.

PRM-0051 has now corrected and offline-validated the flag propagation and the narrow recovery of
that known failed run. Interactive `download` still rejects totals above 20. Do not execute the
public 20→50 retry until PRM-0052 or another explicit human mandate authorizes it.

PRM-0052 consumed that single retry. The retained run advanced 20→50 and stopped cleanly at
`PAUSED / SAFETY_CAP_REACHED`, page/checkpoint 10/10, with all prior hashes preserved and no
residues. This is not evidence of natural provider exhaustion or account completeness. Do not
resume above 50 or run another public command without a new human mandate.

PRM-0053 observed typed provider exhaustion at 22 provider-best artifacts in a new repository.
The durable status correctly became `COMPLETED / PROVIDER_EXHAUSTED`, but the final-page manifest
remained `complete=false` while also recording `exhausted=true`. Treat this as
`REWORK_REQUIRED`; do not repeat the public operation or declare full-account acceptance. A later
offline mandate must reconcile final-page manifest semantics without weakening bounded mode.
