# XMA-CLI-001 release management v1.0.0

Releases follow SemVer and a temporary `release/vX.Y.Z` branch from protected `main`. Scope freezes
at branch creation. Validated feature snapshots are consolidated, fixes are reviewed, and a draft
PR targets main with required CI and resolved conversations.

Candidate preparation builds wheel, sdist and Linux bundle; runs tests, coverage, security scan,
license inventory, SBOM, checksums and Ubuntu 22.04/24.04 portability; and records a handoff. Human
approval is required before squash integration.

Wheel and sdist reproducibility is checked byte-for-byte. The PyInstaller bundle may differ between
builds because its embedded archive is produced by upstream tooling; each candidate is therefore
content-addressed by `SHA256SUMS`, validated after extraction and rebuilt in CI from the locked
source. A difference is documented and never silently substituted.

After integration, create an annotated `vX.Y.Z` tag only at a commit reachable from main. The
manual workflow verifies tag/version, rebuilds artifacts and creates a GitHub Release in **draft**.
A human reviews notes, SBOM, licenses, checksums and artifacts before publication. PyPI publication
requires a separate authorization.

Postrelease verification downloads the published artifacts, checks hashes, extracts the bundle and
runs help/version/status offline. Never rewrite a published tag. For a faulty release, withdraw or
mark artifacts, document impact, revert safely on main and prepare a patch release. Repository
catalog rollback uses backups; migrations are never reversed in place.
