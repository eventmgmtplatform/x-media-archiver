# HND-0015 — B06 public cap-50 recovery v0.5.0

Status: `B06_PUBLIC_LIMIT_50_VALIDATED / FULL_ACCOUNT_PENDING`

## Authorization and baseline

- PRM-0052 authorized exactly one public resume of the retained durable ALL run, from the verified
  total of 20 to an operational cap of 50.
- Baseline head/tree: `7f84812abbe90b7e4cf81ecdd0eb82e52e622029` /
  `8de569a3b639a2e6524aa9ad980bdb4e86c9b5c8`.
- Baseline CI: [41006207235](https://github.com/eventmgmtplatform/x-media-archiver/actions/runs/41006207235),
  SUCCESS; 439 tests; 90.61% CI coverage.
- Branch/PR: `feature/xma-b06-complete-profile-archive`, draft PR #14.
- The publication commit and tree, and the canonical CI over that same tree, are recorded in PR #14
  after the final documentation commit to avoid self-referential evidence.

## Preconditions and failed-run recovery

The retained repository was inside the local home filesystem and passed the read-only preflight:

- 20 videos, 20 sidecars, 20 artifacts, 20 COMPLETED jobs and 20 distinct identities;
- run `FAILED / DomainError`, ALL mode, total 20, page/checkpoint 4/4, cap 50, zero failed items;
- SQLite `integrity_check=ok`, lock free, and zero `.part`/`.tmp` residues;
- aggregate hash `583dd44193c2d2fec37470a0cfcec9ddeba0989d9e25a6e199a3b594c8f61168`;
- 23,653,220,352 bytes available, above both required reserves;
- the single offline status call did not mutate run or checkpoint state;
- the contained Firefox session boundary reported the required session complete without exposing
  selectors or cookie values.

The narrow PRM-0051 recovery recognized only the known compatible ALL failure and resumed the same
run. No repository repair, schema migration, retry, alternate target, profile, or account was used.

## Single public execution

Exactly one `archive --all --resume` command ran with cap 50, batch 5, provider-best quality, the
governed timeouts, and the same `<LOCAL_TARGET>`, `<LOCAL_PROFILE>`, and
`<LOCAL_B06_REPOSITORY>`. It finished with code 0 in 59 seconds.

| Measure | Before | After |
|---|---:|---:|
| verified total | 20 | 50 |
| added this execution | — | 30 |
| videos / sidecars | 20 / 20 | 50 / 50 |
| artifacts / COMPLETED jobs / identities | 20 / 20 / 20 | 50 / 50 / 50 |
| failed total | 0 | 0 |
| page / checkpoint | 4 / 4 | 10 / 10 |
| status / reason | `FAILED / DomainError` | `PAUSED / SAFETY_CAP_REACHED` |
| operational cap | 50 | 50 |
| complete / resumable | false / recoverable by the narrow fix | false / true |

The 20 original files still produce the exact initial aggregate. The final 50-file aggregate is
`090b49f30d9822f7039f3c55baa86d7f07d5df5013caba74e07f0035f3857fb1`.
The retained repository occupies 269,495,611 bytes; 23,470,252,032 bytes remained available.
SQLite integrity is `ok`, every catalog hash and size matches its file and sidecar, the manifest is
complete for the capped operation, the lock is released, and there are no `.part` or `.tmp` files.

This is safety-cap evidence, not provider exhaustion. The account is not declared complete.

## Offline validation and controls

Both pre- and post-execution validation matrices passed:

- `uv sync --locked --all-groups`: PASS;
- Ruff format/check: PASS;
- mypy: PASS;
- pytest: 439 PASS, local coverage 90.28%;
- wheel/sdist build: PASS;
- `git diff --check`: PASS;
- `uv.lock`: byte-identical;
- no media, SQLite, cookie, raw log, or private evidence is tracked by Git.

Raw stdout/stderr were used only to derive sanitized evidence and then removed. The multimedia
repository remains local and intact. There was no second archive, inspect, external disk use,
`<LOCAL_E2E_TARGET>` test, merge, tag, Release, PyPI, Telegram, or WhatsApp activity.

## Limitations and rollback

Natural `PROVIDER_EXHAUSTED` remains publicly unobserved, so full-account completion remains
pending. `RESCAN_DEDUP_V2` may be inefficient at larger totals, and no operation above 50 is
authorized. Roll back the PRM-0051 implementation commit if its narrow recovery must be removed;
preserve the retained repository and do not delete or rewrite verified artifacts.
