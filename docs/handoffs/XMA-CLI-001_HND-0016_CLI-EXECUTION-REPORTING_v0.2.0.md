# HND-0016 — CLI reporting public acceptance v0.2.0

Status: `CLI_REPORTING_PUBLIC_VALIDATED / READY_FOR_MERGE_REVIEW`

## Governance and baseline

- Authority: PRM-0060 v0.1.0, one controlled public acceptance.
- Branch: `feature/xma-cli-execution-reporting`; PR #15.
- Execution HEAD: `d24661b9c1a8003f534c9d38cb5ed890fabae2ef`.
- Execution tree: `db6e69485f46d85fcdc26aab31a64aed942c53ce`.
- Baseline CI: run `41046672992`, `SUCCESS`, 471 tests, 90.89% coverage.
- Handoff baseline: HND-0016 v0.1.1.

The acceptance used only `<LOCAL_E2E_TARGET>`, `<LOCAL_PROFILE>`, the certified
`<LOCAL_E2E_REPOSITORY>`, a new `<LOCAL_REPORTING_REPOSITORY>`, and temporary
`<LOCAL_REPORTING_LOGS>`. Actual selectors and paths are intentionally omitted.

## Acceptance matrix

| Phase | Exit | Duration | Before | New | After | Result |
|---|---:|---:|---:|---:|---:|---|
| Invalid `download --limit 21 --json` | 2 | 0.1 s | n/a | n/a | n/a | One sanitized JSON error; stdout empty; no repository created |
| Human `download --add 1` | 0 | 51.7 s | 0 | 1 | 1 | Exact new-video report and integrity PASS |
| JSON `download --add 2` | 0 | 32.7 s | 1 | 2 | 3 | Additive schema 1 report; `video=null`; integrity PASS |
| Terminal `archive --all --json` no-op | 0 | 5.2 s | 22 | 0 | 22 | Same terminal run/evidence; no provider activity |
| Offline `status --json` | 0 | 0.1 s | 22 | 0 | 22 | Same run/checkpoint; no writes or network |

The retained reporting repository contains three videos, three sidecars, three artifacts, three
COMPLETED jobs, and three distinct identities. SQLite integrity is `ok`; hashes and sizes agree;
the first video remained byte-identical after add 2; there are no `.part` or `.tmp` residues.

Sanitized reporting-repository fingerprints:

- catalog: `8b6880416e882b387df6031e80fb0e8735edcb833f63608ad08ed01d0727dddb`;
- manifest: `be098455c5d062eda15c80742e59d2aeaa77ec329f2fadd72f15337dc1a91876`;
- media aggregate: `bdc0031719e4e00e7b6e687276c97a2f559c57aa8ed6178a074ea6df8eae728f`;
- retained size: 1,167,345,506 bytes.

## Sanitized output evidence

Human output included:

```text
Account: <LOCAL_E2E_TARGET>
Result: COMPLETED
Requested: add 1
Existing before: 0
Downloaded this run: 1
Total after: 1
Video / Post: <PUBLIC_POST_ID> / File: <RELATIVE_ARTIFACT_PATH>
```

The two-video JSON report contained schema 1, command `download`, request `ADD 2`, status
`COMPLETED`, counts 1/2/0/3, `complete=true`, and `video=null`. All legacy download keys remained.
Both successful JSON commands used exactly one stdout object and empty stderr.

## Certified B06 no-op

Before and after both archive and status:

- catalog: `d27c781dba39f7dc7b4cec270ab6cd66493e9b19e0c69653ab91db2d0bae93d2`;
- manifest: `298f186eb526518ccee06a48a36e9a62c02311debc5e24b4d2b246a15c9c28af`;
- media aggregate: `14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.

The 22-video inventory, run ID, timestamps, page/checkpoint 5/5, `COMPLETED /
PROVIDER_EXHAUSTED`, file hashes, sizes, mtimes, catalog, manifest, and sidecars remained
byte-identical. No worker, authentication, extractor, discovery, candidate, duplicate, or download
telemetry was emitted. The lock was released and no file was added, modified, or removed.

## Privacy, retention, and validation

Sanitized outputs were scanned for cookie names/values, Firefox selector, personal paths,
`cookies.sqlite`, signed URLs, sensitive queries, authorization headers, tokens, contact data,
tracebacks, and raw exceptions; no prohibited value was found. Raw logs were deleted only after
sanitized evidence was extracted. `<LOCAL_REPORTING_REPOSITORY>` is retained with all three videos
for Chat/Leonel review. The certified B06 repository remains unchanged.

The final offline validation includes locked sync, Ruff format/check, mypy, full pytest with at
least 471 tests and 90% coverage, build, diff-check, unchanged `uv.lock`/schema/dependencies/
workflows, forbidden tracked-file scan, clean worktree, and final CI. Final documentation SHA/tree
and CI are recorded in the PR body because the handoff cannot contain its own Git object ID without
self-reference.

No retry, alternate target/profile, inspect, sync, exported cookies, external disk, merge, tag,
Release, or PyPI operation occurred. Rollback is the reversal of PR #15; retained local evidence is
not part of Git and requires no migration.
