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
