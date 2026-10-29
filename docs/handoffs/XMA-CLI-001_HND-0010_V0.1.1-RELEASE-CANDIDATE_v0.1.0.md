# XMA-CLI-001 — HND-0010 v0.1.1 release candidate

**State:** IMPLEMENTED / LOCAL_VALIDATED / CI_PENDING

## Governance and baseline

- mandate: PRM-0034 v0.1.0, one human-authorized execution;
- working branch and PR: `hotfix/v0.1.1-download-recovery-quality`, PR #10 draft;
- governance HEAD before edits: `bb598e62c9b23b0fa87a08af4560961bc3550ffc`;
- functional HEAD/tree: `70222dfda922c749457cee1af006b230d103a52d` /
  `90da3a32687da9d16d9509b558d947e24f02d30c`;
- base main: `4ffa3d86a68acc00bb6d729ddf53766959abd6a3`;
- published v0.1.0 target: `c997cce488b4486ffd8dc079cd25819bec402b77`;
- functional CI: run 40959696293, success, 391 tests, 90.63% coverage;
- baseline `uv.lock` SHA-256:
  `593575cb6d76e3bf1fabccccd149809d7b0cc195caf269e1a8c790b234c3ef38`.

## Reconciliation

`Unreleased` is reset to a clean future-development section. The complete v0.1.1 Added, Changed,
Fixed, Security and Known Limitations entries occur exactly once under 0.1.1. README, QUICKSTART,
the local runbook and release notes describe an unpublished validated candidate and make immutable
tag/Release installation conditional on a separate publication decision.

No file under `src/xma`, application test, schema, dependency, workflow or `uv.lock` is changed by
this preparation. Download remains bounded to absolute/additive 1–10, lower limits remain offline
no-ops, quality remains provider-best, and archive remains the durable mechanism capped at ten.

## Changed-file allowlist

- `CHANGELOG.md`;
- `README.md`;
- `QUICKSTART.md`;
- `docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md`;
- `docs/release/XMA-CLI-001_RELEASE-NOTES_v0.1.1.md`;
- Gate Register and Implementation Plan;
- this HND-0010.

## Local validation matrix

- locked sync, Ruff format/check, Ruff lint, mypy and `git diff --check`: PASS;
- pytest: 391 passed, 90.63% total coverage;
- wheel/sdist build and release metadata 0.1.1: PASS;
- pip-audit strict production inventory: no known vulnerabilities;
- license inventory: generated successfully;
- secret and forbidden tracked-file checks: PASS;
- `uv.lock` after validation remains byte-identical to the recorded baseline;
- standalone bundle validation without system Python/uv: PASS;
- CLI help for root, inspect, sync, download, archive and status: PASS;
- `xma version --short`: 0.1.1;
- `SHA256SUMS`, release manifest, license payloads and gallery-dl source: PASS.

## Local release artifact inventory

The local pre-commit build validates packaging mechanics. Final clean-commit artifacts are rebuilt
by the governed RC workflow; their canonical inventory is recorded in PR #10 after CI.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `LICENSE` | 17,984 | `edaef632cbb643e4e7a221717a6c441a4c1a7c918e6e4d56debc3d8739b233f6` |
| `RELEASE-MANIFEST.json` | 1,810 | `686e3b6f5891cd53858710780158c45de96476525fcd9166b851fb91a819c5ba` |
| `THIRD_PARTY_NOTICES.md` | 1,849 | `f48dbe9534526db6e8d485fc351c13ee6187862563323aabaf557713cc54531c` |
| `gallery_dl-1.32.18.tar.gz` | 763,172 | `1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd` |
| `requirements-linux-x86_64.txt` | 14,683 | `a7f6ab131b9a77367680e097dd5c1bac9080ace32cbcc35b5152ea597fa6ff64` |
| `sbom.cdx.json` | 49,884 | `660424d197c769c639d4793633daf08239cc39274108ea8a5548e3ae0e29d765` |
| `x_media_archiver-0.1.1-py3-none-any.whl` | 55,847 | `da40dc04208e5fb7dd17fc449a1fe7d3f6073e9eefba978a4327a676e7c26bb4` |
| `x_media_archiver-0.1.1.tar.gz` | 320,799 | `d31887c4b46464b1416722593b5273fab3f3fc060855275a4c96a738794aaa45` |
| `xma-v0.1.1-linux-x86_64.tar.gz` | 22,836,425 | `7e8679a770677aa21c735980e10485821994260e5a1cd290dcca002d917633d8` |

The bundle includes README, QUICKSTART, LICENSE, THIRD_PARTY_NOTICES and both operating runbooks.
The official gallery-dl source hash matches the governed value. `SHA256SUMS` verifies every
distributed payload and the manifest avoids self-reference.

The final SHA/tree and final quality/Release candidate run URLs/conclusions are recorded canonically
in PR #10 body after both workflows finish, without another evidence commit.

Required candidate evidence includes the standalone Linux bundle without system Python/uv, wheel
and sdist 0.1.1, full `SHA256SUMS`, sanitized `RELEASE-MANIFEST.json`, SBOM, locked requirements,
GPL-2.0-only materials, official gallery-dl 1.32.18 source, and Ubuntu 22.04/24.04 portability.

## Security and rollback

No X, Firefox, cookie, media or local repository is accessed. No private artifact is tracked. The
rollback is a revert of the final release-preparation documentation commit; it does not rewrite the
validated functional history or published v0.1.0 tag.

No merge, tag, GitHub Release, PyPI publication, total above ten, v0.1.2 or v0.2.0 is authorized.
