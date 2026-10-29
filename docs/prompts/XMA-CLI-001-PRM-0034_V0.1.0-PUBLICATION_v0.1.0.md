# XMA-CLI-001-PRM-0034 — v0.1.0 publication v0.1.0

## Human authorization

Leonel authorizes completion and publication of X Media Archiver v0.1.0 on 2026-10-29.

## Mandatory baseline

- Repository: `eventmgmtplatform/x-media-archiver`
- Branch: `release/v0.1.0`
- PR: #6
- Authorized HEAD before this mandate: `63d1b654833302c3202eb618df57b6f4320a9d67`
- PR must remain mergeable and all required CI/RC checks must be green.

## Authorized sequence

1. Add a one-release workflow limited to the authorized squash commit for v0.1.0.
2. Revalidate CI, release-candidate build, security, licenses, checksums and portability.
3. Mark PR #6 ready and squash-merge it into protected `main`.
4. From that exact main commit, create annotated tag `v0.1.0` without rewriting history.
5. Rebuild and validate all release artifacts from the tag source.
6. Publish GitHub Release `XMA v0.1.0` with the governed release notes and all verified assets.
7. Download the published assets, verify `SHA256SUMS`, extract the Linux bundle and run help/version offline.
8. Record postrelease evidence and close superseded PRs #3, #4 and #5.
9. Preserve rollback and patch-release procedures.

## Deferred / prohibited

- GitHub Pages activation and the Pages deployment remain pending.
- PyPI publication requires separate human authorization.
- No access to X, Firefox or cookies.
- No downloads, media generation, schema changes or functional expansion.
- No rewriting `v0.1.0` after publication.

## Failure policy

Fail closed before publication on any mismatch in source SHA, main ancestry, version, tests, security,
license, manifest, checksums or artifacts. If publication completes but postrelease verification
fails, do not rewrite the tag; document the impact and prepare a patch release or withdrawal.
