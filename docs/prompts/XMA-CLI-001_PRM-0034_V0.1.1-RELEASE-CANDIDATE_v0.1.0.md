# XMA-CLI-001-PRM-0034 — V0.1.1 RELEASE CANDIDATE PREPARATION

**Version:** v0.1.0  
**State:** HUMAN_AUTHORIZED / APPROVED FOR ONE EXECUTION  
**Authorized by:** Leonel  
**Date:** 2026-10-29

## Objective

Prepare and validate the X Media Archiver v0.1.1 release candidate from the already validated
hotfix without changing runtime behavior and without publishing the release.

This mandate authorizes documentation reconciliation, local packaging checks and the governed
release-candidate branch/workflow only. It does not authorize X access, public discovery,
downloads, merge, tag, GitHub Release, PyPI or any operation above ten videos.

## Canonical baseline

- Repository: `eventmgmtplatform/x-media-archiver`
- Pull request: #10, open and draft
- Working branch: `hotfix/v0.1.1-download-recovery-quality`
- Functional HEAD: `70222dfda922c749457cee1af006b230d103a52d`
- Functional tree: `90da3a32687da9d16d9509b558d947e24f02d30c`
- Base `main`: `4ffa3d86a68acc00bb6d729ddf53766959abd6a3`
- Published v0.1.0 target: `c997cce488b4486ffd8dc079cd25819bec402b77`
- Handoff: HND-0009 v0.1.0
- CI: run 40959696293, SUCCESS, 391 tests, 90.63% coverage
- Functional decision: `V0.1.1_HOTFIX_VALIDATED / WAITING_CHAT_RELEASE_DECISION`

The governance commit containing this prompt may be newer than the functional HEAD. Codex must
verify that its parent ancestry contains the exact functional HEAD and must not rewrite it.

## Confirmed release-preparation observations

### RC-01 — Release-candidate workflow not executed

The `Release candidate` workflow was skipped because it only builds heads named
`release/v*`, while PR #10 uses a `hotfix/v*` branch. This is not a functional failure, but
standalone bundle and Ubuntu portability evidence are still missing for v0.1.1.

### RC-02 — Changelog duplication

The same v0.1.1 changes currently appear under both `Unreleased` and `0.1.1`. Before release,
`Unreleased` must be reset to a clean future-development section and the complete change set must
exist exactly once under `0.1.1`.

### RC-03 — Candidate wording

README, QUICKSTART, runbook and release notes must remain honest before publication: they may state
that v0.1.1 is a validated release candidate, but must not claim that tag or Release already exists.
The final installation commands may reference the future immutable `v0.1.1` tag and must state
that they apply only after publication.

## Allowlist

Codex may change only release/governance material required for this gate:

- `CHANGELOG.md`
- `README.md`
- `QUICKSTART.md`
- `docs/release/XMA-CLI-001_RELEASE-NOTES_v0.1.1.md`
- `docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md`
- Gate Register and Implementation Plan
- a new HND-0010 release-candidate handoff
- PR #10 body
- release packaging scripts/workflows only if an offline or RC validation proves a narrow
  v0.1.1 packaging defect

Codex may create or fast-forward `release/v0.1.1` to the final validated hotfix commit after all
documentation changes are committed. The release branch must point to exactly the same final commit
as PR #10 head when the final RC workflow is evaluated.

## Prohibited changes and actions

Do not:

- modify `src/xma/**`, runtime behavior, database schema or application tests;
- add or update dependencies;
- change `uv.lock`;
- access X, Firefox, browser profiles, cookies or public media;
- run inspect, sync, download, archive or any smoke against X;
- create, upload or track media, SQLite, private manifests, raw logs, cookies or credentials;
- merge PR #10;
- mark PR #10 ready for review;
- create or move a tag;
- create or publish a GitHub Release;
- publish to PyPI;
- start v0.1.2, v0.2.0, mass download, Telegram or WhatsApp work.

If a functional defect is discovered, stop with `REWORK_REQUIRED`; do not fix it under this
mandate.

## Required execution

### 1. Baseline and ancestry

Before editing:

- confirm PR #10 is open, draft and mergeable;
- confirm the current branch contains functional HEAD `70222df...`;
- confirm the functional tree matches `90da3a3...`;
- confirm CI run 40959696293 is green;
- confirm no untracked private evidence is present;
- confirm the worktree is clean;
- record the current branch HEAD and tree.

Stop on any mismatch.

### 2. Reconcile release documentation

- Keep an empty/clean `Unreleased` section for future work.
- Move the complete v0.1.1 Added, Changed, Fixed, Security and Known Limitations entries under
  `[0.1.1] - 2026-10-29` exactly once.
- Preserve comparison links:
  - `Unreleased`: `v0.1.1...HEAD`
  - `0.1.1`: `v0.1.0...v0.1.1`
- Describe v0.1.1 as a validated RC, not as already published.
- Preserve the global maximum of ten videos and the distinction between interactive `download`
  and durable `archive`.
- Preserve the exact semantics:
  - `download --limit 1..10` is an absolute desired total;
  - `download --add 1..10` is additive;
  - the resulting verified total cannot exceed ten;
  - lower absolute limits are offline no-ops;
  - quality is `provider-best`;
  - operation above ten is not supported in v0.1.1.

### 3. Local release validation

Run without X/network use except normal official dependency/package sources already required by the
release build:

```bash
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
uv run python scripts/verify-release-metadata.py
git diff --check
```

Also run the existing vulnerability, license, secret/forbidden-file and release-manifest controls.
Confirm:

- all tests pass;
- total coverage remains at least 90%;
- wheel and sdist report version 0.1.1;
- `uv.lock` is byte-identical to the baseline;
- no functional file changed;
- no private artifact is tracked;
- worktree is clean after commits.

### 4. Prepare the RC branch

After the final documentation/handoff commit:

1. Create `release/v0.1.1` if absent, pointing to the final PR #10 head.
2. If it already exists, inspect it and only fast-forward it when ancestry is valid; never force
   push and never rewrite history.
3. Push the branch once to trigger `Release candidate`.
4. Do not create a second release branch or an additional candidate.

### 5. Required RC evidence

The final `Release candidate` workflow must run on the exact final commit/tree and pass:

- build on Ubuntu 22.04;
- standalone Linux x86_64 bundle;
- execution without system Python or uv;
- `xma --help` and `xma version --short == 0.1.1`;
- command help for inspect, sync, download, archive and status;
- SHA256SUMS verification;
- RELEASE-MANIFEST validation;
- wheel and sdist 0.1.1;
- SBOM and locked requirements;
- GPL-2.0-only license and third-party notices;
- official gallery-dl 1.32.18 source with the governed SHA-256;
- portability on Ubuntu 22.04 and Ubuntu 24.04.

The normal quality workflow for PR #10 must also be green on the exact same final commit.

### 6. Evidence and handoff

Publish:

- `HND-0010 V0.1.1-RELEASE-CANDIDATE v0.1.0`;
- final SHA and tree;
- changed-file inventory;
- local validation matrix;
- quality CI run;
- RC workflow run and job results;
- release artifact inventory, sizes and SHA-256 values;
- bundle version/portability evidence;
- confirmation that no X access, download, merge, tag, Release or PyPI occurred.

To avoid an evidence-only commit loop, HND-0010 may state that final GitHub run URLs and conclusions
are recorded canonically in PR #10 body. Update the PR body only after the final workflows complete;
do not commit again afterward.

## Final states

Exactly one:

- `V0.1.1_RC_READY / WAITING_CHAT_PUBLICATION_DECISION`
- `V0.1.1_RC_BLOCKED`
- `REWORK_REQUIRED`

## Stop condition

After both final workflows complete and PR #10 body is reconciled:

- stop;
- keep PR #10 draft and open;
- do not merge;
- do not tag;
- do not create or publish a Release;
- do not publish PyPI;
- report the final state to Leonel and wait for a separate publication decision.
