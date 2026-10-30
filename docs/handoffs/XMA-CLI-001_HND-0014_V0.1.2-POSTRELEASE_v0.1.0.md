# XMA-CLI-001 — HND-0014 v0.1.2 postrelease

**State:** `V0.1.2_POSTRELEASE_CLOSED / PROJECT_STABLE`

## Published baseline

- Product: X Media Archiver `0.1.2` — `RELEASED`.
- Public date: `2026-10-30T01:54:22Z` (`CHANGELOG` release date: `2026-10-29`).
- Published main: `d595bd61e2d1642b6d6ba889de63b29d98307b85`.
- Published tree: `c0c3b975a323484731795f0781e74c40cee6b378`.
- Annotated tag: `v0.1.2`, object `8c09cb67b2bb46132a8100df0e6ab7482c3b9979`, targeting published main.
- GitHub Release: ID `428531308`, <https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.2>.
- Release inventory: ten assets with complete `SHA256SUMS`; PyPI is not published.
- This documentation branch starts from the published main. Its final squash commit, tree, and CI
  remain externally fixed by the postrelease PR to avoid a self-referential documentation cycle.

## Released scope

v0.1.2 contains:

- sanitized classification of HTTP/media failures;
- one bounded URL renewal and controlled internal second attempt;
- continued scan after failed media candidates and per-command exclusion of failed identities;
- active discovery deadline excluding consumer download/persistence time;
- pending IPC message drainage before timeout classification;
- `download --limit 1..10`, `download --add 1..20`, and maximum verified total twenty;
- durable `archive --limit 20`;
- provider-best quality selection;
- opt-in local public harness and accepted public progression `0 → 5 → 10 → 20`.

The public acceptance did **not** produce a DownloadError. Continuation after a failed candidate is
validated by deterministic offline tests and is not represented as publicly observed.

## Verification

- Local suite: 405 tests passed.
- Coverage: 90.67%, above the required 90%.
- Ruff format/check: PASS.
- mypy: PASS.
- wheel and sdist build: PASS.
- release metadata 0.1.2: PASS.
- Ubuntu 22.04 and 24.04 release validation: PASS.
- standalone Linux x86_64 bundle: PASS.
- SBOM, GPL-2.0-only license, third-party notices, gallery-dl corresponding source, manifest, and
  checksums: PASS.
- `git diff --check`: PASS.
- `uv.lock`: byte-identical to published main.
- Diff allowlist: Markdown documentation only; no source, tests, workflows, dependencies, schema,
  lockfile, media, SQLite, cookies, manifests, logs, or private evidence.

The retained multimedia acceptance evidence remains exclusively under `<LOCAL_XMA_DATA_ROOT>`, is
not tracked by Git, and was not read, copied, modified, deleted, packaged, or published during this
reconciliation.

## Pending work and boundaries

- GitHub Pages/Actions remains administratively disabled or pending; this closure does not enable it.
- PyPI remains unpublished.
- Telegram and WhatsApp remain future roadmap items requiring separate governance.
- Bulk support, scheduler, and an efficient remote cursor remain deferred.
- v0.2.0 has not started; no v0.1.3 or other version is inferred.
- Published tags must never be moved or deleted.

## Rollback

Operational rollback is to install and use published `v0.1.1`, preserving repositories and taking a
full backup before any compatibility action. Do not rewrite `v0.1.2`, reverse SQLite migrations in
place, or delete evidence. Documentation rollback is the squash-revert of the postrelease-only PR;
it does not alter the published tag, Release, or assets.

## Closure

After the documentation PR passes CI and is squash-merged, update main by fast-forward and verify
main CI. Only then remove the obsolete hotfix, release, and postrelease documentation branches and
prune remote-tracking references. No force-push, tag deletion, Pages activation, PyPI publication,
or next-version work is authorized.
