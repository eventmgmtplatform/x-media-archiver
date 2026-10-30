# HND-0012 — active discovery deadline and scan continuation

**State:** V0.1.2_MEDIA_RECOVERY_VALIDATED / WAITING_CHAT_VALIDATION

## Baseline and delivery

- Baseline SHA: `f08d6afe6927690c14b94222d42efbf7a76cd8bb`.
- Baseline tree: `a971dcb6f5800c635a2dd1251febf07edee6e802`.
- Functional SHA: `037def6fe69555bde5e65efbafc8f6acde7d1671`.
- Functional tree: `46bef8557303154b2b6b9098a4686f56c0618d23`.
- Branch: `hotfix/v0.1.2-media-recovery`; PR #12 remained open and draft.
- Functional CI: run 40973378281, SUCCESS.
- `uv.lock` remained byte-identical; no dependency, schema, or workflow changed.

## Confirmed causes and correction

R-06 was reproduced at the incremental IPC boundary: a single absolute deadline continued advancing while the generator was suspended at `yield`, so media transfer, hashing, sidecar creation, and SQLite persistence consumed discovery time. The provider now measures the suspension interval and extends the active deadline by exactly that interval. Pending Pipe messages are polled and drained before timeout classification. Real idle time remains bounded; WORKER_FAILED, terminate, kill fallback, and join behavior remain intact.

R-07 was reproduced in `DownloadService.execute_incremental`: `DownloadError` broke out of the candidate stream. A failed candidate is now cleaned, persisted as FAILED_FINAL with a constant sanitized code, counted, and excluded from later candidates and from the second bounded discovery attempt. Consumption continues to later identities without retrying the failed identity inside the command.

Before the fix, PRM-0039 consistently stopped after three integral assets with WORKER_FAILED for requests of five or more. After the fix, the controlled acceptance completed 0→5→10→20 without increasing the configured discovery timeout.

## Offline validation

- Focused deadline and continuation tests: 55 passed.
- Complete suite: 405 passed.
- Coverage: 90.67%.
- Ruff format/check: PASS.
- mypy: PASS.
- build: PASS.
- `git diff --check`: PASS.
- Added regressions cover consumer suspension longer than discovery timeout, real provider timeout, pending IPC drain, terminal processing, failed-identity exclusion, multiple failures with later success, exhausted partial progress, cleanup, manifests, jobs, and artifacts.

## Public acceptance matrix

The same authorized target and `<LOCAL_PROFILE>` were used through `.venv/bin/xma`. Each command ran exactly once with provider-best quality, max-scan 500, discovery timeout 30 seconds, two bounded discovery attempts, and an external maximum of 300 seconds.

| Phase | Exit | Existing | New | Total | Failed | Complete | Artifacts/jobs | SQLite | Residues |
|---|---:|---:|---:|---:|---:|---|---|---|---:|
| limit 5 | 0 | 0 | 5 | 5 | 0 | true | 5/5 | ok | 0 |
| add 5 | 0 | 5 | 5 | 10 | 0 | true | 10/10 | ok | 0 |
| add 10 | 0 | 10 | 10 | 20 | 0 | true | 20/20 | ok | 0 |

The final repository contains twenty distinct identities, twenty MP4 files, twenty sidecars, twenty artifacts, and twenty COMPLETED jobs. Earlier phase hashes remained identical after both later phases. No public candidate failed during this acceptance, while offline tests prove continuation and sanitized FAILED_FINAL persistence for failed candidates.

## Retention, space, and security

- Repository retained at `<LOCAL_XMA_DATA_ROOT>/prm-0040-incremental-acceptance/`.
- Sanitized evidence retained under `<LOCAL_XMA_DATA_ROOT>`.
- Retained repository size: 5,885,457,155 bytes.
- Data-volume available before: 103,377,084,416 bytes.
- Data-volume available after: 97,491,496,960 bytes.
- Raw logs were removed only after sanitized summaries and hashes were captured.
- Videos, sidecars, manifests, SQLite, and SHA-256 evidence were retained.
- No `.part` or `.tmp` remains.
- No profile name, cookie, signed URL, header, token, or personal path is published.
- Earlier PRM-0039 media evidence remains `EVIDENCE_NOT_RETAINED_BEFORE_STORAGE_ADDENDUM` and was not reconstructed.

## Risk and rollback

The deadline remains finite and measures only active provider/IPC wait; consumers can legitimately extend wall-clock duration while processing a yielded candidate. Failed identities are command-local exclusions and can be reconsidered by a future independently authorized command. Rollback is `git revert 037def6fe69555bde5e65efbafc8f6acde7d1671`; retained local evidence must not be removed by rollback.

No merge, tag, Release, PyPI, dot, alternate profile/target, or operation above twenty occurred.
