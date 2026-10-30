# CERT-0001 — B06 complete-profile archive v0.1.0

Decision: `VALIDATED_WITH_OBSERVATIONS`

## Certified scope

B06 certifies the development `archive --all` slice for one observed public account: durable
checkpoints, resumable safety caps, provider-best artifacts, typed provider exhaustion, normalized
catalog/sidecars/manifest, and completely offline status inspection. It does not change the
published v0.1.2 contract.

Functional baseline: PR #14, PRM-0053 public execution, PRM-0054 manifest-semantics correction, and
PRM-0055 evidence reconciliation. PRM-0053 made exactly one public request sequence and produced 22
intact assets before typed `ProviderExhaustedError` completed the durable run.

## Certified evidence

- Durable state: `COMPLETED / PROVIDER_EXHAUSTED`, goal `PROVIDER_EXHAUSTION`, complete true,
  resumable false, total 22, failed total 0, page/checkpoint 5/5, operational cap 30.
- Repository: 22 videos, sidecars, artifacts, COMPLETED jobs, and distinct identities.
- Quality: provider-best.
- SQLite: `integrity_check=ok`.
- Media aggregate: `14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.
- Manifest before reconciliation:
  `50eb3de528146dac46896f66632723995caa8a7b71960cf1f24426ddb0be2324`,
  `complete=false / exhausted=true`.
- Manifest after atomic reconciliation:
  `298f186eb526518ccee06a48a36e9a62c02311debc5e24b4d2b246a15c9c28af`,
  `complete=true / exhausted=true`.
- Catalog hash remained
  `d27c781dba39f7dc7b4cec270ab6cd66493e9b19e0c69653ab91db2d0bae93d2`.
- Logical manifest comparison proved that `complete` was the only changed field; run timestamps,
  catalog, artifacts, sidecars, hashes, sizes and checkpoint remained unchanged.
- Zero `.part`/`.tmp`, lock released, no secrets or signed URLs in public evidence.

The final PR head/tree and CI are recorded in PR #14 after the documentation commit. Validation
includes at least 442 tests, ≥90% coverage, Ruff, mypy, build, metadata and forbidden-file checks.

## Observations, risk, and rollback

- `RESCAN_DEDUP_V2` can be inefficient at large scale.
- This certifies one observed public account, not every X account or provider behavior.
- Authentication depends on a pre-existing local Firefox session and remains fail-closed.
- Thousands of downloads, mass/unattended operation, a scheduler, and an efficient remote cursor
  are not certified.
- Telegram and WhatsApp remain future roadmap work.
- PRM-0056 `CLI-EXECUTION-REPORTING` remains backlog and is not implemented.

Operational rollback restores the preserved original manifest atomically after verifying its hash;
it does not delete artifacts, rewrite catalog state, or move published tags. Any rollback requires a
separate governed decision.
