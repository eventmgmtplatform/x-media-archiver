# XMA-CLI-001-PRM-0046 — B06 offline boundary hardening v0.1.0

Status: `HUMAN_AUTHORIZED / EXECUTED_ONCE`

## Scope

Leonel authorized one exclusively offline rework on PR #14. The governed baseline was
`8afa7f1b74ec0fb2edc3fdf114832467bad64718`, tree
`83145c190e26bbb3d5a3130b51e4f0c0de3ff2b1`, based on main
`82c28396d442057ef00c48293001f75fb4116861`. Public access, Firefox, cookies, real
profiles, external disks, merge, tags, releases, PyPI, Telegram, and WhatsApp were prohibited.

## Required corrections

1. Replace string matching for provider exhaustion with an explicit domain signal translated only
   from the real provider exhaustion terminal. BOUNDED behavior must remain unchanged.
2. Make ALL status expose provider exhaustion as its goal, without a fictitious numeric target or
   remaining count. A safety cap is operational, remains resumable, and never means completion.
3. Compare `max_items` against verified target-scoped repository state before discovery or run
   mutation. A lower cap fails closed; an equal cap pauses without network; a higher cap proceeds.
4. Persist unexpected failures as `FAILED / UNEXPECTED_FAILURE`, retain the original only as an
   internal cause, and expose a stable sanitized XMA error at the real CLI boundary.
5. Reconcile ADR-0007, the B06 runbook, Gate Register, Implementation Plan, PR #14, and
   HND-0015 v0.1.1 with CI on the final published head/tree.

## Acceptance

The locked environment, Ruff formatting and linting, mypy, the complete pytest suite with at least
90% coverage, build, and `git diff --check` must pass. Dependencies remain unchanged; no private or
runtime evidence may be tracked. Stop at
`B06_OFFLINE_HARDENED / PUBLIC_ACCEPTANCE_PENDING`, with PR #14 still draft.
