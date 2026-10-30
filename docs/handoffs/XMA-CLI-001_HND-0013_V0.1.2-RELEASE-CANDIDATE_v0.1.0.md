# XMA-CLI-001 — HND-0013 v0.1.2 release candidate

**State:** V0.1.2_RC_READY / WAITING_CHAT_PUBLICATION_DECISION

## Baseline and included commits

- Baseline: `3f5c6ce5e30d70de7f8a48a1058baad714e74c20`, tree
  `46525d5590ffd5e0fbdb89a66a2b3c9cd0a7a1cb`.
- Functional media-recovery commit: `037def6fe69555bde5e65efbafc8f6acde7d1671`.
- PRM-0040 handoff commit: `3f5c6ce5e30d70de7f8a48a1058baad714e74c20`.
- RC preparation commit: `835c4c4`.
- Standalone bundle-name correction: `604a45e68748760dd611b6fecadbe5278fb52693`;
  payload tree `58b27a74401ba50cf1390fd1b82b4bccfa4ac4fa`.
- Branch/PR: `hotfix/v0.1.2-media-recovery`, PR #12 open and draft.

The final delivery SHA/tree and final CI/RC run links are recorded in the PR body after the last
commit, avoiding a documentation-only commit cycle.

## Release scope

The candidate contains sanitized HTTP/media failure codes, one bounded URL renewal path, scan
continuation after failed media candidates, command-local exclusion of failed identities, an active
provider/IPC deadline that excludes consumer time, pending IPC drain, download absolute limits
1–10, additive requests 1–20, a maximum verified total of twenty, archive through twenty,
provider-best quality, an opt-in local acceptance harness, and public evidence 0→5→10→20.

**Required observation:** the public acceptance produced no DownloadError. Continuation after a
failed candidate is validated by deterministic offline tests and is not claimed as publicly
observed.

## Files and documentation

Release metadata, `CHANGELOG.md`, `README.md`, `QUICKSTART.md`, the local runbook, release notes,
Gate Register, Implementation Plan, license/third-party description, build/validation scripts,
manifest generator, PyInstaller spec, CI, release-candidate workflow, and draft-release workflow
were reconciled for 0.1.2. No download/discovery runtime behavior, SQLite schema, or production
dependency changed during PRM-0041.

`uv.lock` has one unavoidable mechanical delta: the editable root project version changes from
0.1.1 to 0.1.2. Every resolved dependency and hash is unchanged. Keeping the file byte-identical
would make `uv sync --locked` and wheel metadata inconsistent with the authorized 0.1.2 version.

## Validation

- `uv sync --locked --all-groups`: PASS.
- Ruff format/check: PASS.
- mypy: PASS.
- pytest: 405 passed; total coverage 90.67%.
- wheel/sdist metadata and `xma version --short`: 0.1.2.
- isolated wheel installation in Python 3.12: PASS.
- standalone bundle without system Python/uv: PASS.
- `pip-audit --strict`: no known vulnerabilities.
- license inventory and CycloneDX SBOM: PASS.
- complete GPL-2.0-only license in wheel, sdist, and bundle: PASS.
- official `gallery_dl-1.32.18.tar.gz`: SHA-256
  `1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd`, PASS.
- sanitized `RELEASE-MANIFEST.json` and complete `SHA256SUMS`: PASS.
- forbidden tracked-file and secret scans: PASS.
- Ubuntu 22.04/24.04 portability: supplied by the final release-candidate workflow.

## Stable payload inventory

These payload hashes exclude the self-updating manifest/checksum metadata and remain stable when
this handoff is added because `docs/handoffs/**` is excluded from the sdist and bundle.

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `LICENSE` | 17,984 | `edaef632cbb643e4e7a221717a6c441a4c1a7c918e6e4d56debc3d8739b233f6` |
| `THIRD_PARTY_NOTICES.md` | 1,849 | `2e995484a0e099035806bc06f21ae5eb3557922914261458cce41412e6455ed1` |
| `gallery_dl-1.32.18.tar.gz` | 763,172 | `1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd` |
| `requirements-linux-x86_64.txt` | 14,683 | `a7f6ab131b9a77367680e097dd5c1bac9080ace32cbcc35b5152ea597fa6ff64` |
| `sbom.cdx.json` | 49,884 | `660424d197c769c639d4793633daf08239cc39274108ea8a5548e3ae0e29d765` |
| `x_media_archiver-0.1.2-py3-none-any.whl` | 56,227 | `d59393737b94f0680cd519d1c31893f303e2c7186967948c777af0f472f28728` |
| `x_media_archiver-0.1.2.tar.gz` | 326,162 | `527f4106134506c0f00c00ea2759eaac34f48461731ceaf13694bdb79574c170` |
| `xma-v0.1.2-linux-x86_64.tar.gz` | 22,836,898 | `8d5f522e21f31ace9da539d529cdeeeee7e4bdb7d9b2d37bf1bf0f26e3220785` |

The final `RELEASE-MANIFEST.json` and `SHA256SUMS` hashes are reported in the PR body after the
final-commit rebuild. The manifest never hashes itself; `SHA256SUMS` binds it and every distributed
asset.

## Evidence, risk, and rollback

The retained PRM-0040 multimedia repository remains exclusively under `<LOCAL_XMA_DATA_ROOT>` and
was not read, copied, modified, deleted, packaged, or published during RC preparation.

Residual limits remain: maximum twenty, Linux x86_64, no mass operation, no scheduler, and provider
availability outside XMA. Rollback is to revert the RC preparation and bundle-name commits while
leaving functional commit `037def6` and retained local evidence untouched.

No X/Firefox/cookie access, new download, merge, tag, GitHub Release, PyPI publication, or later
version was performed.
