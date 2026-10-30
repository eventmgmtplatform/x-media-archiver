# HND-0016 — CLI invocation reporting semantics v0.1.1

Status: `CLI_REPORTING_INVOCATION_SEMANTICS_VALIDATED / PUBLIC_ACCEPTANCE_PENDING`

## Governance and baseline

- Authority: PRM-0061, one completely offline execution.
- Branch: `feature/xma-cli-execution-reporting`; draft PR #15.
- Initial HEAD: `e0cb57abf42aa2e7af9707a8bf857e56862e3800`.
- Initial tree: `0497026fe7c8f60377a59de62f8272b7aedfb9e5`.
- Initial CI: run `41032298392`, `SUCCESS`, 463 tests.
- Functional repair commit: `308e79c85dd6e54f37497e2380b4bc61d2a51985`.
- Functional tree: `626f3dcf462ca9e5256389d757c3bd1d32f009aa`.

PRM-0060 was not executed or consumed. No X, Firefox, cookies, public request, or real multimedia
repository was accessed.

## Design

`ArchiveService.execute()` publishes the verified repository total through a narrow optional
callback immediately after successful verification. The CLI stores that integer only in the active
invocation and passes it to the reporting layer. It is neither added to nor inferred from the
durable `ArchiveRun`, and the SQLite schema is unchanged.

The report calculation is:

```text
downloaded_this_run = total_after - invocation_verified_before
```

`status` is an offline query, so it uses the durable total it just read as its invocation baseline
and reports zero current work. If execution fails before verification invokes the callback, the
report does not reuse historical durable values: `downloaded_this_run=null` and
`progress_available=false`.

## Required offline matrix

| Scenario | Verified before | Total after | Downloaded this run |
|---|---:|---:|---:|
| Initial archive | 0 | 22 | 22 |
| Existing bounded archive | 5 | 10 | 5 |
| Resume | 10 | 20 | 10 |
| Partial failure | 10 | 13 | 3 |
| Provider exhaustion | 20 | 22 | 2 |
| Terminal no-op | 22 | 22 | 0 |
| Offline status | 22 | 22 | 0 |

Every row is covered by deterministic offline regression tests. A real CLI failure before
verification additionally proves the null/unavailable contract and empty stdout for JSON errors.

## Compatibility and privacy

No existing JSON key, report schema version, exit code, human mode, archive mode, operational
limit, provider-exhaustion behavior, checkpoint, or durable field changed. No schema, migration,
dependency, `uv.lock`, workflow, authentication, discovery, IPC, downloader, or media behavior
changed. Reports remain sanitized and contain no profile selectors, cookies, tokens, signed URLs,
absolute paths, raw exceptions, or traceback.

## Verification and rollback

- Ruff format/check: PASS.
- mypy: PASS.
- Full pytest: PASS, 471 tests, 90.49% local coverage.
- Functional regression matrix: PASS.
- Final build, diff-check, forbidden-file scan, commit/tree and CI are recorded in the draft PR
  after the documentation commit to avoid self-referential Git evidence.

Rollback is the reversal of the two PRM-0061 commits. It requires no data migration because the
baseline exists only in process memory and no durable contract changed.
