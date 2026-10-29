# ADR-0005 — Durable incremental archive

**Status:** Accepted for B05 v0.1.0  
**Date:** 2026-10-29

## Decision

B05 adds `xma archive` and offline `xma status`. Archive accepts PROFILE targets, totals 1–10,
batches 1–5 and fixed page intervals 1–60 seconds. It keeps the B04 synchronous downloader and
spawn/Pipe discovery boundary.

Durable pagination uses `RESCAN_DEDUP_V1`: each page rescans the profile, skips catalog identities,
persists at most `batch_size` new candidates, then commits its checkpoint. No opaque remote cursor
is invented. The strategy is adequate for the governed ten-item slice but inefficient for thousands.

Schema v2 adds `archive_runs` and `archive_checkpoints`; existing artifacts remain the canonical
identity set. `next_allowed_at` preserves cooldown across processes. In-process pacing also uses a
monotonic clock and injectable sleeper. Linux `flock` prevents concurrent archive writers.

## Safety and consequences

Checkpoints advance only after DownloadService confirms each page. Existing artifacts are verified
before discovery and never overwritten. Provider failures pause the run with a sanitized error code.
Status is read-only and never performs network access. No cookies, browser selector, personal path,
media URL, header, token or raw exception enters the checkpoint.

Rollback is code rollback plus retaining schema v2 tables; migration is monotonic and preserves B04
catalogs. Dropping v2 tables is not automated because it could erase durable run evidence.
