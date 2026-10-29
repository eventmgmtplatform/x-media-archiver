# XMA-CLI-001 — HND-0009 v0.1.0 download recovery and quality

**State:** V0.1.1_HOTFIX_VALIDATED / WAITING_CHAT_RELEASE_DECISION

## Baseline

- `origin/main`: `4ffa3d86a68acc00bb6d729ddf53766959abd6a3`.
- published `v0.1.0` target: `c997cce488b4486ffd8dc079cd25819bec402b77`.
- branch: `hotfix/v0.1.1-download-recovery-quality`.
- authority: PRM-0032 v0.1.0 plus Addendum 001 v0.1.1.

## Defects and decisions

The exact failed database shape (completed discovery, one media asset, `FAILED_FINAL` job with one
attempt, zero artifacts and no files) previously failed reconciliation. It now remains auditable and
can transition explicitly to a second queued/downloading attempt. Only completed jobs require an
artifact; unexpected final/staging/sidecar files, artifact without completed job, and completed job
without artifact remain conflicts.

Lower absolute totals are offline no-ops. Additive mode computes from the verified target-scoped
repository total. Both modes accept 1–10, remain mutually exclusive and fail before network when
the result would exceed ten. Discovery is bounded by max-scan, worker count and timeout.

`best` maps to the provider's best direct variant and persists only `provider-best`, dimensions,
MIME, extension, size and hash. A second bounded worker may refresh the ephemeral URL after one
media failure; no URL is persisted.

## Changed files and regression evidence

The functional commit is `c16bcd76396d2b0c0c4b8d1260cc5e584c296236` (tree
`bb2c11c7f98cd7925abde2740cf59352a96ce40f`). It changes the download application/CLI, the
incremental gallery-dl boundary, narrow domain retry behavior, tests, v0.1.1 metadata/release
automation, and the governed documentation listed by PR #10. There is no schema or dependency
change; `uv.lock` changes only the local project version from 0.1.0 to 0.1.1.

The exact failed shape was reproduced with one `FAILED_FINAL` job at attempt one, zero artifacts and
no residue. Before the fix reconciliation rejected it; after the fix an explicit retry completed at
attempt two with exactly one verified artifact. Separate fixtures retain fail-closed behavior for an
unexpected file, a completed job without artifact and an artifact without completed job. Fixtures
also cover second-worker URL refresh, max-scan exhaustion, cleanup, lower-limit no-op, additive
totals, every accepted 1–10 value, above-ten preflight rejection and B02–B05 regressions.

## Local and CI validation

- locked sync, Ruff format/check, mypy, build and `git diff --check`: PASS;
- pytest: 391 passed, total coverage 90.63%;
- wheel and sdist: 0.1.1; release metadata: PASS;
- forbidden tracked-file scan: no media, SQLite, cookies, private manifests or logs;
- functional CI run [40958909181](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/40958909181):
  SUCCESS on the functional SHA, 391 tests and 90.63% coverage.

## Public acceptance matrix

Exactly four authorized commands ran once against one new repository with Firefox authentication,
quality best, max-scan 100, two bounded discovery attempts and a 30-second worker deadline. No
manual retry occurred.

| Operation | Exit | Existing | Downloaded | Total | Complete |
| --- | ---: | ---: | ---: | ---: | --- |
| `--add 1` | 0 | 0 | 1 | 1 | true |
| `--add 1` | 0 | 1 | 1 | 2 | true |
| `--add 3` | 0 | 2 | 3 | 5 | true |
| `--limit 1` | 0 | 5 | 0 | 5 | true |

Final evidence has five distinct completed identities, five artifacts, five MP4 files and five
sidecars. SQLite `integrity_check` is `ok`; file sizes and SHA-256 values match the catalog;
`quality_policy=provider-best`, MIME, extension and dimensions are present; `.part`/`.tmp` count is
zero. The final lower-limit operation performed zero discovery and zero HTTP download.

Textual evidence and SQLite text fields contain no cookie names/values, selector, signed media URL,
headers or tokens. Media, database, logs and local paths remain exclusively local and untracked.

## Remaining observations and rollback

Provider-best is the best direct variant selected by gallery-dl; it is not a resolution guarantee.
The global v0.1.1 cap remains ten, and this evidence does not certify mass download, scheduling or
operation above ten. Final documentation SHA/tree and final CI are recorded in PR #10 after the last
commit to avoid a self-referential evidence commit.

No local path, Firefox selector, cookie, signed URL, media, SQLite or raw log may be published.
Rollback is a revert of the hotfix commit; completed repositories are never rewritten.
