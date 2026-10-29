# XMA-CLI-001-PRM-0027 — B05 Durable Archive Slice v0.1.0

**Authority:** Leonel  
**Baseline:** B04 `a745f3ce1ea637aca04917da1a9aabb7d05414a8`  
**Branch:** `feature/xma-b05-durable-archive`  
**State on completion:** `WAITING_CHAT_VALIDATION`, partial/blocked, or rework required

## Mandate

Close B04 as `VALIDATED_WITH_OBSERVATIONS`, then implement an incremental durable archive with
PROFILE-only `archive`, offline `status`, schema-v2 checkpoints, `RESCAN_DEDUP_V1`, fixed rate
limiting, resumption, filesystem/catalog integrity checks and a recoverable single-writer lock.

Limits are total 1–10, batch 1–5, interval 1–60 seconds. Existing B04 download behavior, Firefox
read-only authentication, spawn/Pipe IPC, atomic staging, immediate persistence and sanitized
outputs remain intact. No new dependency, cookie export, scheduler, parallel download, ORM, Redis,
Docker, API, GUI, yt-dlp or FFmpeg is authorized.

After offline tests, coverage ≥90 % and CI green, migrate the exact five-asset BBCWorld repository
offline and run status. Then execute exactly one authenticated archive command to total 10 with
batch 2, interval 2 and discovery timeout 30. Run status offline afterward. Do not retry.

Publish ADR-0005, HND-0005 v0.1.0, README/CHANGELOG/governance/plan updates and draft PR #5 stacked
on draft PR #4. Stop after final CI. No dot, merge, tag, release, B06 or operation above ten.
