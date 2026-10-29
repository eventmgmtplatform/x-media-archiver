# HND-0012 — v0.1.2 public matrix harness recovery

**State:** MATRIX_EXECUTED / PUBLIC_ACCEPTANCE_PARTIAL / EVIDENCE_RETENTION_DEVIATION / WAITING_CHAT_VALIDATION

## Baseline and scope

- Baseline SHA: `68a4602a23ee9d85923ae511a5dd1e06caa702eb`.
- Baseline tree: `1183fae79ecca535bce9e3f389ec951a1f92a97f`.
- Branch: `hotfix/v0.1.2-media-recovery`; PR #12 remained open and draft.
- Baseline CI: run 40969998738, SUCCESS.
- Earlier deleted evidence remains `EVIDENCE_NOT_RETAINED_AFTER_AUTHORIZED_CLEANUP`.
- No R-01–R-05 functional code, dependency, schema, workflow, or `uv.lock` change was made by PRM-0039.

The acceptance harness was repaired to invoke `.venv/bin/xma` directly. Before the matrix, `uv sync --locked --all-groups` passed and `.venv/bin/xma version --short` returned `0.1.1`. Public cases did not use `uv run` and no command was retried manually.

## Sanitized matrix

All repositories started empty and used the same authorized target and `<LOCAL_PROFILE>`. `quality=best`, `max-scan=500`, a 180-second external timeout, and at most one command per case were enforced.

| Case | Exit | Seconds | Downloaded | Skipped | Failed | Total | Artifacts/jobs | SQLite | Residues | Classification | Captured size (bytes) |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|
| limit-1 | 0 | 15 | 1 | 0 | 0 | 1 | 1/1 | ok | 0 | SUCCESS | 220305778 |
| limit-2 | 0 | 69 | 2 | 0 | 0 | 2 | 2/2 | ok | 0 | SUCCESS | 1117651548 |
| limit-3 | 0 | 112 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | SUCCESS | 1940194185 |
| limit-5 | 5 | 110 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | WORKER_FAILED | 1940192717 |
| limit-10 | 5 | 110 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | WORKER_FAILED | 1940192722 |
| limit-20-negative | 2 | 0 | 0 | 0 | 0 | 0 | 0/0 | not created | 0 | INVALID_INPUT | 57 |
| add-1 | 0 | 14 | 1 | 0 | 0 | 1 | 1/1 | ok | 0 | SUCCESS | 220305778 |
| add-2 | 0 | 63 | 2 | 0 | 0 | 2 | 2/2 | ok | 0 | SUCCESS | 1117651548 |
| add-3 | 0 | 113 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | SUCCESS | 1940194185 |
| add-5 | 5 | 112 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | WORKER_FAILED | 1940192717 |
| add-10 | 5 | 108 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | WORKER_FAILED | 1940192722 |
| add-20 | 5 | 108 | 3 | 0 | 0 | 3 | 3/3 | ok | 0 | WORKER_FAILED | 1940192722 |

The negative limit-20 case created no catalog and was rejected before discovery. Values add-1 through add-20 were accepted. Cases through total three completed; requests for five or more preserved three integral assets and ended with the sanitized `WORKER_FAILED` terminal. No `.part` or `.tmp` residue was observed. The matrix therefore does not validate the requirement that a failed media candidate allow continued scanning to later identities.

## Storage addendum timing

The storage addendum was received after add-20 had already completed. Under the instruction active when the matrix began, every disposable repository and raw log had already been removed immediately after sanitized evidence extraction. Therefore videos, sidecars, manifests, and catalogs cannot be retained or moved retroactively and were not reconstructed or downloaded again.

After receipt, `<LOCAL_XMA_DATA_ROOT>` was verified as an accessible writable data volume with 1,000,186,310,656 bytes capacity and 103,377,084,416 bytes available, exceeding the revised 50 GiB preflight. An exclusive PRM-0039 directory was created without modifying pre-existing content, and the sanitized matrix was retained there. Per-case measurements in the table were taken on the original filesystem before the addendum; data-volume before/after values are `EVIDENCE_NOT_CAPTURED_BEFORE_ADDENDUM`.

## Security, cleanup, and rollback

- No profile name, cookie, signed media URL, header, token, personal path, or raw log is published.
- No manual retry, merge, tag, Release, PyPI, dot, or operation above 20 occurred.
- Raw logs and disposable repositories were removed before the storage addendum arrived.
- Rollback is limited to reverting the harness-only commit; R-01–R-05 remain unchanged.
- Human review is required before any further public execution.
