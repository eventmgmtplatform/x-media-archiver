# HND-0015 — B06 offline boundary hardening v0.1.1

Status: `B06_OFFLINE_HARDENED / PUBLIC_ACCEPTANCE_PENDING`

## Governance and baseline

- Authorization: PRM-0046, one offline execution only.
- Governed head: `8afa7f1b74ec0fb2edc3fdf114832467bad64718`.
- Governed tree: `83145c190e26bbb3d5a3130b51e4f0c0de3ff2b1`.
- Base main: `82c28396d442057ef00c48293001f75fb4116861`.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- Baseline CI: 40998451403, SUCCESS; 422 tests; 90.42% coverage.

## Delivered corrections

- R-01: provider exhaustion is a typed domain signal translated only from the worker's natural
  exhaustion terminal. A transient error containing the legacy marker cannot complete ALL.
- R-02: ALL publishes `goal=PROVIDER_EXHAUSTION`, null numeric target/remaining, and a distinct
  operational cap. Completion requires `COMPLETED / PROVIDER_EXHAUSTED`; v2/v3 reads remain safe.
- R-03: verified target-scoped state is compared with the cap before discovery or run mutation.
  The 20-existing matrix for caps 10, 20, 21, and 50 is covered offline.
- R-04: unexpected failures persist `FAILED / UNEXPECTED_FAILURE` and cross the real CLI boundary
  as a constant typed error with exit code 5, no traceback or raw provider/local data.
- R-05: PRM-0046, ADR-0007, the runbook, Gate Register, Implementation Plan, handoff index, and
  this addendum are reconciled without rewriting historical evidence.

## Files and decisions

Functional changes are limited to archive/discovery domain signaling, application boundaries,
SQLite compatibility reads, CLI status/error presentation, and their offline tests. Schema,
dependencies, workflow, authentication, download transport, and published v0.1.2 behavior are
unchanged. `uv.lock` remains byte-identical.

## Validation

- `uv sync --locked --all-groups`: PASS.
- `uv run ruff format --check .`: PASS.
- `uv run ruff check .`: PASS.
- `uv run mypy`: PASS.
- `uv run pytest`: 429 PASS; local coverage 90.20%.
- `uv build`: PASS.
- `git diff --check`: PASS.
- Tracked-file review: no media, SQLite, logs, cookies, secrets, or local evidence.

The canonical final CI is the required quality run attached to this handoff's containing PR #14
HEAD/tree. Its immutable run URL, conclusion, final commit, and final tree are reconciled in the PR
body after CI completes, avoiding an evidence-only commit loop. That run—not baseline CI—is the
acceptance evidence for this addendum.

## Limitations, risk, and rollback

No public acceptance, provider account, Firefox session, cookie, external disk, or media was used.
Real provider exhaustion and public 20→50 acceptance remain pending. Roll back the bounded code
commit and restore a pre-migration catalog backup when applicable; never delete verified media.
PR #14 remains draft. No merge, tag, release, PyPI, Telegram, or WhatsApp work is authorized.
