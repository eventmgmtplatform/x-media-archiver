# CERT-0001 — B06 complete-profile archive v0.1.1

Decision: `VALIDATED_WITH_OBSERVATIONS / COMPLETE_PROFILE_CERTIFIED`

## Certified scope

B06 certifies the development `archive --all` slice for one observed public account: durable
checkpoints, resumable safety caps, provider-best artifacts, typed provider exhaustion, normalized
catalog/sidecars/manifest, offline status, and terminal idempotency after confirmed exhaustion. It
does not change the published v0.1.2 contract.

The functional baseline is PR #14 through PRM-0057. PRM-0053 produced 22 intact assets before
typed provider exhaustion; PRM-0054 corrected manifest semantics; PRM-0055 reconciled and certified
the retained evidence; PRM-0058 then executed exactly one public terminal repetition.

## Certified evidence

- Durable state before and after: `COMPLETED / PROVIDER_EXHAUSTED`, goal
  `PROVIDER_EXHAUSTION`, total 22, failed total 0, page/checkpoint 5/5.
- Repository before and after: 22 videos, sidecars, artifacts, COMPLETED jobs and distinct
  identities; provider-best; SQLite `integrity_check=ok`; zero `.part`/`.tmp`.
- Media aggregate before and after:
  `14269cd54b4695d3069c5eeae453714e17573d3082b3e9e352c1cce13eea5c05`.
- Reconciled manifest before and after:
  `298f186eb526518ccee06a48a36e9a62c02311debc5e24b4d2b246a15c9c28af`.
- Catalog before and after:
  `d27c781dba39f7dc7b4cec270ab6cd66493e9b19e0c69653ab91db2d0bae93d2`.
- The governed repetition finished code 0 in 4.872 seconds and returned the same run, state,
  checkpoint, timestamps, historical caps and verified total 22.
- Full inventory comparison found zero added, removed or changed evidence files. No worker,
  authentication, extractor, discovery, profile, video, candidate or duplicate event was emitted;
  no download occurred and the repository lock was released.

The public execution used source head/tree `1605fd0b6af974c67298abd89d27a299597fbb65` /
`fbd12d90fc5e43aece7c07b8dec4767b7f9db4f9`. The final documentary head/tree and CI are recorded
in PR #14 after this certification is committed.

CERT-0001 v0.1.0 remains immutable historical evidence. No target, Firefox selector, local path,
cookie, signed URL, raw log or media file is published here.

## Observations, risk and rollback

- Terminal repetition does not refresh an exhausted account. Refresh requires a future explicit
  mode and separate governance; silently converting repetition into discovery is prohibited.
- This certifies one observed public account, not every provider/account behavior.
- `RESCAN_DEDUP_V2` may be inefficient at scale; thousands of downloads, scheduler and unattended
  operation remain uncertified.
- Firefox authentication remains an external dependency for non-terminal operations.

Rollback reverts only PRM-0057 and the PRM-0058 documentation. It requires no catalog migration,
artifact rewrite or evidence repair. Published tags and retained evidence must not be moved.
