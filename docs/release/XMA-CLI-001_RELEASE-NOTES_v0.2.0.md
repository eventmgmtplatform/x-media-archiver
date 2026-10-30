# X Media Archiver v0.2.0 release notes

**Status:** validated release candidate; not tagged or published.

v0.2.0 extends the bounded v0.1.2 downloader with durable complete-profile archive and structured
execution reporting while preserving the local-first, privacy-preserving architecture.

## Included

- discovery, SQLite cataloging, exact-post and profile downloads;
- absolute LIMIT and additive ADD with provider-best quality;
- durable BOUNDED and ALL archive, checkpoints, resumption, rate limiting and offline status;
- typed provider exhaustion, explicit safety caps and terminal idempotent no-op;
- human execution summaries and additive JSON `report_schema_version=1`;
- exact detail for one newly downloaded video and compact aggregate reporting for two or more;
- invocation-scoped progress, durable checkpoint, sanitized terminal reason and resumability;
- contained read-only Firefox authentication without cookie export;
- normalized filesystem repository, sidecars, manifests, SHA-256 and SQLite integrity.

## Operational boundaries

Interactive download supports `--limit 1..10`, `--add 1..20`, and a verified maximum total of 20.
BOUNDED archive is capped at 20. ALL archive requires an explicit operational safety cap; validation
of one observed account and a 50-item safety-cap run does not certify mass or unattended use.

Linux x86_64 on Ubuntu 22.04 and 24.04 is the certified platform. Windows, macOS, scheduler, GUI,
API service, Telegram, WhatsApp, efficient remote cursor, PyPI and bulk operation are not included.

## Distribution and verification

The candidate contains a wheel, sdist, standalone bundle, locked requirements, CycloneDX SBOM,
GPL-2.0-only license, third-party notices, official gallery-dl 1.32.18 source,
`RELEASE-MANIFEST.json`, and `SHA256SUMS`. Verify with `sha256sum -c SHA256SUMS` before use.

Publication requires a separate human decision. This preparation creates no tag, GitHub Release or
PyPI publication.
