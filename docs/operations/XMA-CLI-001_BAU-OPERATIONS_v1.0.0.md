# XMA-CLI-001 BAU operations v1.0.0

## Purpose, scope and roles

This runbook operates bounded local XMA repositories up to ten videos. The operator installs,
runs, verifies, backs up and preserves evidence. The maintainer diagnoses defects, reviews
dependencies and prepares governed releases. Neither role expands scope without authorization.

## Start-of-operation checklist

1. Confirm Linux x86_64, available disk and writable local filesystem with `flock`.
2. Verify `xma version` and `xma --help`; confirm the expected release SHA/checksum.
3. Confirm repository backup and no `.part`/`.tmp` residue.
4. For authenticated work, confirm Firefox/profile access without exporting cookies.
5. Run `xma status --repository REPOSITORY --json` offline and review state/integrity.

## Installation and operation

Extract the approved bundle, verify `SHA256SUMS`, then use `./xma`. Source/wheel alternatives are
documented in the local CLI runbook. Examples:

```bash
./xma download @HANDLE --limit 1 --repository REPOSITORY --auth-browser firefox --auth-profile PROFILE
./xma download @HANDLE --limit 2 --repository REPOSITORY --auth-browser firefox --auth-profile PROFILE
./xma download @HANDLE --limit 5 --repository REPOSITORY --auth-browser firefox --auth-profile PROFILE
./xma archive @HANDLE --limit 10 --batch-size 2 --repository REPOSITORY \
  --auth-browser firefox --auth-profile PROFILE --request-interval 2 --discovery-timeout 30
./xma download https://x.com/HANDLE/status/POST_ID --limit 1 --repository REPOSITORY \
  --auth-browser firefox --auth-profile PROFILE
./xma status --repository REPOSITORY --json
```

Exit 0 means success. Governed nonzero codes are sanitized contract/provider/catalog/download or
usage failures; preserve the code and terminal classification, never raw session data. Use command
help for the exact version’s code descriptions.

## Integrity, backup, restore and resumption

Back up catalog, artifacts, sidecars and manifests together after a clean stop. Restore into a new
empty local directory, verify `PRAGMA integrity_check`, file sizes and SHA-256, then run offline
status. `PAUSED` may resume with identical target/configuration; `FAILED` requires maintainer
diagnosis. Never overwrite or reconstruct valid evidence casually.

## Cleanup, retention and rotation

Delete only verified temporary `.part`/`.tmp` files after a stopped process; never delete cataloged
artifacts to “fix” state. Retain evidence according to organizational policy, encrypt backups and
rotate whole repository snapshots. Do not retain exported cookies or signed URLs.

## Update and rollback

Freeze operation, back up, verify the new bundle/checksums, test help/version/status offline, then
open the repository. Roll back the executable and restore the pre-update repository snapshot if a
migration or integrity check fails. Never downgrade a catalog in place.

## Troubleshooting and incidents

- Authentication/session: stop; verify contained Firefox availability without exposing values.
- Provider timeout/rate limit: preserve `PAUSED`; do not unbounded-retry.
- Catalog/filesystem/hash mismatch: classify integrity incident and fail closed.
- Secret exposure, corrupted evidence or unexpected network behavior: security incident; isolate
  logs, stop operation and follow SECURITY.md.
- Packaging/CLI startup defect: operational incident; record version, checksum and sanitized error.

Escalate to the maintainer with version, command class, exit code, sanitized status, integrity
result and artifact counts. Never attach cookies, signed URLs, profile paths or private logs.

## End-of-operation checklist

1. Confirm terminal state is not `RUNNING` and lock is released.
2. Run offline status and integrity checks; confirm no `.part`/`.tmp`.
3. Verify artifact/sidecar counts, sizes and hashes; create a complete backup.
4. Store sanitized operational evidence and remove temporary logs according to retention policy.
