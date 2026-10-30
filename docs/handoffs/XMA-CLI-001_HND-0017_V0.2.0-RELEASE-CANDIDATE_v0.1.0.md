# XMA-CLI-001 — HND-0017 v0.2.0 release candidate

**State:** `V0.2.0_RC_READY / WAITING_CHAT_PUBLICATION_DECISION`

## Baseline and authorization

- Authority: PRM-0063 v0.1.0, one release-candidate preparation.
- Baseline main: `4cf2bda4ff5e333df3fca5b8f75cc4788b4ef304`.
- Baseline tree: `9cde2812d39cef0f02950dca657c789224c9d97e`.
- Baseline CI: run 41052068663, SUCCESS, 471 tests, 90.89% coverage.
- Branch: `release/v0.2.0`; draft PR `release: prepare XMA v0.2.0`.

No retained multimedia repository was inspected or modified. No X, Firefox, cookie, public download,
merge, tag, GitHub Release or PyPI operation is part of this handoff.

## Authorized diff

- Promote project and runtime metadata from `0.2.0.dev0` to `0.2.0`.
- Update the editable project entry in `uv.lock` only; all dependency versions, sources and hashes
  remain identical.
- Reconcile changelog, README, quick start, runbook, wiki, release notes, governance, planning and
  handoff index.
- Update existing RC build/manifest/validation automation only for v0.2.0 asset names, inventory,
  metadata and Ubuntu portability.

There are no runtime behavior, SQLite schema/migration, production dependency or discovery changes.

## Release scope

The candidate includes discovery/catalog, exact and profile downloads, LIMIT/ADD, provider-best,
durable BOUNDED/ALL archive, checkpoints, resumption, rate limiting, typed provider exhaustion,
terminal no-op, offline status, human and JSON schema 1 reports, precise one-video detail, aggregate
multi-video summaries, sanitized failure/progress reporting, read-only Firefox authentication and
the normalized SQLite/filesystem repository.

The release remains Linux x86_64 only and bounded. It does not provide mass/unattended operation,
scheduler, GUI, API, Telegram, WhatsApp, efficient remote cursor, Windows/macOS certification or
PyPI distribution.

## Validation and distribution

The governed validation covers locked sync, Ruff, mypy, full pytest with at least 471 tests and 90%
coverage, wheel/sdist build, metadata, isolated Python 3.12 wheel install, standalone bundle without
checkout/Python/uv dependency, negative offline CLI validation, pip-audit, license inventory,
GPL-2.0-only payloads, official gallery-dl source, SBOM, manifest, checksums and forbidden files.

CI validates the same final tree on Ubuntu 22.04 and 24.04. The final SHA/tree, CI runs, exact asset
sizes/hashes and reproducibility comparison are recorded in the draft PR body after the final commit,
avoiding a self-referential handoff/manifest cycle.

Rollback before publication is deletion of the unmerged release branch/PR. After any separately
authorized publication, rollback means use the immutable v0.1.2 release; published tags must never
be moved.
