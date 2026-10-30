# HND-0015 — B06 completed-account public no-op v0.8.0

Status: `B06_PUBLIC_NOOP_VALIDATED / COMPLETE_PROFILE_CERTIFIED / READY_FOR_MERGE_REVIEW`

## Authorization and baseline

- PRM-0058 authorized exactly one public `archive --all` repetition against the already certified
  account and retained 22-artifact repository.
- Execution head/tree: `1605fd0b6af974c67298abd89d27a299597fbb65` /
  `fbd12d90fc5e43aece7c07b8dec4767b7f9db4f9`.
- Baseline CI: [41028798895](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41028798895),
  SUCCESS; 451 tests; 90.91% coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Final documentary commit/tree and canonical CI are reconciled in PR #14 after the commit to
  avoid self-referential evidence.

The target, Firefox selector and repository remained local and are represented only as
`<LOCAL_E2E_TARGET>`, `<LOCAL_PROFILE>` and `<LOCAL_E2E_REPOSITORY>`.

## Preflight and single execution

Offline preflight found exactly one repository matching all certified fingerprints. It contained
22 videos, sidecars, artifacts, COMPLETED jobs and distinct identities; provider-best; durable
`COMPLETED / PROVIDER_EXHAUSTED`; goal `PROVIDER_EXHAUSTION`; failed total 0; page/checkpoint 5/5;
SQLite `ok`; no residues; lock available.

Exactly one non-resume `archive --all` command used the compatible historical cap and parameters.
It returned code 0 in 4.872 seconds with the same run ID, terminal state, verified total 22,
page/checkpoint 5/5, timestamps, cooldown and historical caps. No retry, inspect, sync, download,
second archive, alternate target/profile or external storage was used.

## Before/after evidence matrix

| Evidence | Before | After |
| --- | ---: | ---: |
| Verified total | 22 | 22 |
| Videos / sidecars | 22 / 22 | 22 / 22 |
| Artifacts / COMPLETED jobs / identities | 22 / 22 / 22 | 22 / 22 / 22 |
| Durable terminal | `COMPLETED / PROVIDER_EXHAUSTED` | unchanged |
| Page / checkpoint | 5 / 5 | 5 / 5 |
| failed total | 0 | 0 |
| SQLite integrity | `ok` | `ok` |
| Added / changed / removed files | 0 / 0 / 0 | 0 / 0 / 0 |
| `.part` / `.tmp` | 0 / 0 | 0 / 0 |

Fingerprints were byte-identical before and after:

- catalog: `d27c781dba39f7dc7b4cec270ab6cd66493e9b19e0c69653ab91db2d0bae93d2`;
- manifest: `298f186eb526518ccee06a48a36e9a62c02311debc5e24b4d2b246a15c9c28af`;
- media aggregate: `14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.

The command emitted no `WORKER_STARTED`, `AUTH_LOADED`, `EXTRACTOR_STARTED`, `PROFILE_SEEN`,
`VIDEO_SEEN`, `CANDIDATE_SENT`, `DUPLICATE_SKIPPED` or discovery-attempt event. Standard error was
empty. The final lock check succeeded. Catalog/manifest/media/sidecars, file sizes, hashes, mtimes,
run timestamps and checkpoint remained unchanged. Raw logs were sanitized and removed.

## Documentation, validation and CI

Documentation files:

- `README.md`;
- `docs/wiki/b06-complete-profile-archive.md`;
- `docs/certifications/XMA-CLI-001_CERT-0001_B06-COMPLETE-PROFILE-ARCHIVE_v0.1.1.md`;
- `docs/handoffs/XMA-CLI-001_HND-0015_B06-COMPLETE-PROFILE-ARCHIVE-SLICE_v0.8.0.md`.

The final local matrix includes locked sync, Ruff format/check, mypy, the complete pytest suite,
wheel/sdist build and diff-check. Exact final test count, coverage, documentary SHA/tree and CI are
recorded in PR #14 on completion. `uv.lock`, source, schema, dependencies and workflows remain
unchanged; no local media, SQLite, manifest, cookie, secret or raw log is tracked.

## Limitation and rollback

This proves terminal idempotency for the certified retained account. It does not authorize or
implement refresh semantics. A future account refresh requires an explicit distinct mode and human
authorization.

Rollback reverts the documentary commit and, only if separately authorized, the PRM-0057
functional commit. No retained evidence, catalog, artifact or published tag is modified.
