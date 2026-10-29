# HND-0012 — v0.1.2 media recovery and add20

**State:** TEST_EVIDENCE_FAILED / REWORK_REQUIRED

- Baseline: `30ae2e6685504593db5f49adf2f2f79d7b9a3335`, tree `38558cb129471a9833caf32b46711ae7e42c5195`.
- Branch: `hotfix/v0.1.2-media-recovery`.
- Previous disposable repositories were removed by Leonel before resumption; hashes are `EVIDENCE_NOT_RETAINED_AFTER_AUTHORIZED_CLEANUP`.
- Disk preflight after cleanup: 23.85 GB available; revised 15 GiB gate PASS.
- HTTP failures are mapped to constant MEDIA_* codes and never expose source URLs.
- Download absolute limit remains 1–10; additive request and final repository maximum are 20; archive maximum is 20.
- Quality remains provider-best; no FFmpeg, yt-dlp or transcoding.

Offline validation: 399 tests passed, 90.60% coverage; Ruff format/check, mypy, build and diff check passed. CI quality run 40969760695 passed on functional commit `3c7303798e3a7212d2edee251c36815bf14d15f3` (tree `e04e02a75ba07e9dca0648769f68af579866c1e2`).

The authorized public matrix stopped at the first LIMIT 1 invocation. Before XMA started, `uv` failed to create a temporary cache file because its configured cache filesystem was read-only. Exit code was 2 and elapsed time rounded to zero seconds. The disposable repository remained empty: authentication was not loaded, no provider or discovery worker was constructed, and no access to X occurred. In accordance with the no-retry rule, LIMIT 1 was not repeated and no later LIMIT or ADD case ran.

Space before the invocation was 23,834,128,384 bytes and after it was 23,846,002,688 bytes, both above the 5 GiB floor. The empty disposable repository was removed after sanitized evidence capture. The earlier repositories removed by Leonel remain `EVIDENCE_NOT_RETAINED_AFTER_AUTHORIZED_CLEANUP`; no hashes were reconstructed. Evidence is retained at `<LOCAL_EVIDENCE_DIR>`. No real profile, cookie, media URL, raw log, or personal path is published.
