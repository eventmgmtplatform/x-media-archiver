# HND-0012 — v0.1.2 media recovery and add20

**State:** IMPLEMENTED / OFFLINE_VALIDATED / CI_PENDING / PUBLIC_ACCEPTANCE_PENDING

- Baseline: `30ae2e6685504593db5f49adf2f2f79d7b9a3335`, tree `38558cb129471a9833caf32b46711ae7e42c5195`.
- Branch: `hotfix/v0.1.2-media-recovery`.
- Previous disposable repositories were removed by Leonel before resumption; hashes are `EVIDENCE_NOT_RETAINED_AFTER_AUTHORIZED_CLEANUP`.
- Disk preflight after cleanup: 23.85 GB available; revised 15 GiB gate PASS.
- HTTP failures are mapped to constant MEDIA_* codes and never expose source URLs.
- Download absolute limit remains 1–10; additive request and final repository maximum are 20; archive maximum is 20.
- Quality remains provider-best; no FFmpeg, yt-dlp or transcoding.

Offline validation: 399 tests passed, 90.60% coverage; Ruff format/check, mypy, build and diff check passed. Final SHA/tree, CI and sanitized public matrix are recorded after validation. No real profile, cookie, media URL or personal path is published.
