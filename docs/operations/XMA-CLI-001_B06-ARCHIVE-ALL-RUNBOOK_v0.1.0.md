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

`PROVIDER_EXHAUSTED` is the only successful completion reason for ALL. `SAFETY_CAP_REACHED`,
`MAX_RUNTIME_REACHED`, `LOW_DISK_SPACE`, `INTERRUPTED`, and `PROVIDER_TRANSIENT` are resumable
pauses. `FAILED` requires offline integrity diagnosis. `--resume` fails closed unless a compatible
ALL run is paused. `RESCAN_DEDUP_V2` rescans and deduplicates; it is not a remote cursor.

Back up the whole repository before migration. Never delete or overwrite verified artifacts.
Public acceptance and complete-account operation remain pending.
