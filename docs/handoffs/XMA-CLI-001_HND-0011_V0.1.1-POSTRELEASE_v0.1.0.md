# XMA-CLI-001 — HND-0011 v0.1.1 postrelease

**State:** V0.1.1_PUBLISHED / POSTRELEASE_RECONCILED

## Immutable release evidence

- main release commit: `9490dbdfd43517a08c68745147d3a6d34d23af25`;
- product tree: `f5a154687d984d0e50596a8daf17b7a4bd565dda`;
- annotated tag: `v0.1.1`, object `286a6aaa9580c5c19cc46f23f48e58f423c15be5`;
- GitHub Release ID: `428434769`;
- public URL: https://github.com/eventmgmtplatform/x-media-archiver/releases/tag/v0.1.1;
- published at: `2026-10-29T21:59:03Z`;
- Release state: public, non-draft, non-prerelease;
- public assets: ten;
- public `SHA256SUMS`: PASS;
- standalone bundle: `xma version --short == 0.1.1`;
- PyPI: intentionally unpublished.

## Public artifact anchors

- bundle: `63b53cfd04ff47119330a44197bac15cc6d68e028fbaed3b41a96b8fbaba525a`;
- wheel: `da40dc04208e5fb7dd17fc449a1fe7d3f6073e9eefba978a4327a676e7c26bb4`;
- sdist: `d31887c4b46464b1416722593b5273fab3f3fc060855275a4c96a738794aaa45`;
- manifest: `67210e7a0d6e45a1850ee9b5f9eef39648fd19852e5fe8e75eb4edb42448ce3b`;
- SBOM: `660424d197c769c639d4793633daf08239cc39274108ea8a5548e3ae0e29d765`;
- gallery-dl source: `1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd`.

## Postrelease reconciliation

README, QUICKSTART, runbook, release notes and product wiki now describe v0.1.1 as published and
link the immutable Release. Gate Register and Implementation Plan record PRM-0035, PRM-0036 and
this closure. No functional source, test, schema, dependency, workflow, package, tag, Release asset
or lockfile is changed.

GitHub Pages remains `PAGES_ACTIVATION_PENDING`; this does not affect the public GitHub Release.
Mass download, PyPI, Telegram, WhatsApp and subsequent versions remain outside this gate.

## Rollback

The documentation-only squash commit may be reverted independently. The published tag and Release
must not be moved, replaced or deleted as part of documentation rollback.
