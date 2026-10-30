# HND-0015 — B06 complete-profile archive slice v0.1.0

Status: `B06_OFFLINE_READY / PUBLIC_ACCEPTANCE_PENDING`

## Baseline and authorization

- Baseline: `82c28396d442057ef00c48293001f75fb4116861`
- Tree: `c2c3da45f3d5525cd8dadb3c57b8bd0847456fb0`
- Branch: `feature/xma-b06-complete-profile-archive`
- Addendum 01 cancelled OPS-0002, external-volume inspection, PRM-0040 evidence, and public access.

## Delivered design

- Functional commit: `12368521837da1b62a5fcac8374cabaff921e9d2`.
- Functional tree: `300764f902f98df5ecace57e13d5d8cffd79f0a3`.

- `ArchiveMode`: `BOUNDED`, `ALL`.
- Completion reasons distinguish requested total, provider exhaustion, safety cap, runtime, disk,
  interruption, provider transient failure, and terminal failure.
- `RESCAN_DEDUP_V2` retains target-scoped verified identities and checkpoints only persisted pages.
- `--resume` requires a compatible paused ALL run.
- SQLite v3 transactionally migrates v2 archive state and records ALL durability fields.
- `status` exposes sanitized mode, reason, verified/failed totals, checkpoint, safety controls,
  elapsed time, resumability, and completion without network access.
- Project development version: `0.2.0.dev0`; dependencies unchanged.

## Validation

- `uv sync --locked --all-groups`: PASS.
- Ruff, mypy: PASS.
- Full suite: 421 PASS; coverage 90.08%.
- Synthetic 20→50: PAUSED / SAFETY_CAP_REACHED; no public media.
- Provider exhaustion, low disk, max runtime, interruption, resume, migration, status,
  target-scoped reconciliation, bounded archive, download, and SINGLE_POST regressions: PASS.

The final documentation commit, tree, and CI URL are reconciled in PR #13 without another
functional change.

## Limitations and rollback

Public 20→50 acceptance, real provider exhaustion, and full-account archive were not executed.
RESCAN_DEDUP_V2 can be inefficient at scale. Roll back code and restore a pre-migration SQLite
backup; never delete verified media. No X, Firefox, cookies, external disk, or public download was
accessed.
