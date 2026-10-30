# XMA-CLI-001 — HND-0018 v0.2.0 release metadata rework

**State:** `V0.2.0_RELEASE_METADATA_REWORK_READY / WAITING_ASSET_REPAIR_AUTHORIZATION`

## Baseline and authorization

- Authority: PRM-0065 v0.1.0, one offline metadata rework.
- Baseline main: `462eca59f9754776c26b748ed0fbeaf93ceb11db`.
- Baseline tree: `3a64dbd5ad3750e17cae81d735be871a319e61cc`.
- Existing annotated tag: `v0.2.0`; object
  `33a1d7b98b91b2b02b72faf3f89c47ddd5b257de`; target is baseline main.
- Existing GitHub Release draft: ID 429267623, ten uploaded assets, unpublished.
- Branch: `hotfix/v0.2.0-release-metadata`; independent draft PR.

The operation does not move or recreate the tag, modify the draft, replace assets, publish GitHub
Release/PyPI, access X/Firefox/cookies, download media, or inspect retained multimedia repositories.

## Confirmed defects and correction

The original manifest omitted the release tag and described only its eight hashed payloads without
an explicit ten-asset release contract. The official workflow also selected historical v0.1.2
release notes.

The generator now resolves the tag fail-closed from explicit `RELEASE_TAG`, or from
`GITHUB_REF_TYPE=tag` plus `GITHUB_REF_NAME`. It accepts exactly `v0.2.0`, rejects branch refs,
empty/invalid tags and tag/version mismatches, and does not infer a tag from the package version.
The workflow passes the authorized tag explicitly and validates the exact non-empty v0.2.0 notes
before building.

## Deterministic 10/8/2 contract

The release contains ten uniquely named assets:

- eight payloads with size and SHA-256 in `artifacts`;
- `RELEASE-MANIFEST.json` as the manifest control asset, verified by `SHA256SUMS`;
- `SHA256SUMS` as the checksum-index control asset, whose digest is supplied externally by the
  GitHub Release asset record.

The manifest declares `release_asset_count=10`, `payload_asset_count=8`,
`control_asset_count=2`, the exact ten-name inventory, roles and digest policies. Control entries
deliberately omit size/digest fields. This avoids both a manifest self-hash and the cycle that would
arise if the manifest hashed `SHA256SUMS` while `SHA256SUMS` hashes the manifest.

Build order is payloads, manifest, then `SHA256SUMS`. The checksum index contains exactly nine
unique entries: the eight payloads plus the manifest. It excludes itself. Validation checks all
payload sizes/digests, the exact 10/8/2 inventory, control roles, nine checksum entries and every
referenced digest.

## Tests and local validation

- 25 deterministic metadata tests cover tag resolution/rejection, 10/8/2 inventory, missing,
  extra and duplicate payload/control entries, size/hash mismatches, nine checksums, absence of
  cycles, v0.2.0 release-note selection, v0.1.2 rejection and privacy.
- Full suite: 496 tests passed; total coverage 90.49%.
- Locked sync, Ruff format/check, mypy, build and `git diff --check`: PASS.
- Project metadata remains 0.2.0.
- `uv.lock` remains byte-identical at
  `a74e3b47a0f06455019950f8d530bd31cc483bb8414a1a63e06878a53e670744`.
- `src/xma`, schema, migrations, dependencies and functional behavior are unchanged.

A temporary build outside Git produced exactly ten assets. Its manifest declared tag v0.2.0,
the source commit/tree, 10/8/2 counts and eight payloads. `SHA256SUMS` contained exactly nine
entries and `sha256sum -c SHA256SUMS` passed. Temporary artifacts are removed after validation.

## Files and traceability

Functional commit: `decd799d6fc001aed2355da17823ee7fdf5ac252` (tree
`e3626b574fbc13749e230a4c6f7b18e86472559a`). It changes only:

- `.github/workflows/release.yml`;
- `scripts/generate-release-manifest.py`;
- `tests/test_release_metadata.py`.

This documentation commit adds HND-0018 and the handoff index entry. The final branch SHA/tree and
the canonical CI run on that exact HEAD are recorded in the draft PR body after CI, avoiding an
impossible self-reference inside the commit that names itself.

Rollback before asset repair is closing the unmerged hotfix PR. The existing tag and draft remain
immutable. Replacing the draft assets, merging the hotfix, rerunning the release workflow, or
publishing requires a separate human authorization.
