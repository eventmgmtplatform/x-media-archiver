# XMA v0.2.0 quick start

> v0.2.0 is a validated release candidate, not yet tagged or published. `archive --all` is validated
> with observations for one public account and is not certified for mass or unattended operation.

## Install and verify

After publication, obtain the v0.2.0 assets, verify `SHA256SUMS`, extract the Linux
x86_64 bundle, and verify the embedded CLI:

```bash
tar -xzf xma-v0.2.0-linux-x86_64.tar.gz
cd xma-v0.2.0-linux-x86_64
./xma --help
./xma version --short
```

The version must be `0.2.0`. The bundle needs neither Python nor `uv`. Before extraction, verify
the distributed `SHA256SUMS` from the parent directory with `sha256sum -c SHA256SUMS`.

## Firefox authentication

Authenticated commands read an existing Firefox session through XMA's read-only boundary. Supply
only a contained Firefox profile **name**, never its path:

```text
--auth-browser firefox --auth-profile PROFILE_NAME
```

Do not export cookies or use a cookie file. Authentication fails closed when the selected session
does not contain the required values. XMA does not persist cookies, headers, tokens, signed media
URLs, or the local profile selector.

## Bounded downloads

Download a total of one, two, or five videos from a public profile:

```bash
./xma download @HANDLE --limit 1 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME
./xma download @HANDLE --limit 2 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME
./xma download @HANDLE --limit 5 --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME
./xma download @HANDLE --limit 10 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME
./xma download @HANDLE --add 1 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME
./xma download @HANDLE --add 5 --repository ./repository-HANDLE \
  --quality best --max-scan 100 --auth-browser firefox --auth-profile PROFILE_NAME
```

Download one exact public status without scanning the profile:

```bash
./xma download "https://x.com/HANDLE/status/POST_ID" --limit 1 \
  --repository ./repository-single-post \
  --auth-browser firefox --auth-profile PROFILE_NAME
```

Query strings and fragments are removed from a valid status URL. Other hosts, HTTP URLs, shortened
links, extra path elements, author mismatches, and post-ID mismatches fail closed.

## Durable archive, status, and resumption

Archive progressively up to the supported maximum of twenty videos:

```bash
./xma archive @HANDLE --limit 20 --batch-size 2 \
  --repository ./repository-HANDLE \
  --auth-browser firefox --auth-profile PROFILE_NAME \
  --request-interval 2 --discovery-timeout 30
```

Inspect the durable state offline:

```bash
./xma status --repository ./repository-HANDLE
./xma status --repository ./repository-HANDLE --json
```

`COMPLETED` means the requested total is present. `PAUSED` preserves confirmed progress and may be
resumed with compatible arguments. `FAILED` requires integrity diagnosis before another run.
Re-running a compatible operation deduplicates verified artifacts rather than overwriting them.

Complete-profile archive requires an explicit safety cap:

```bash
uv run xma archive @HANDLE --all --max-items 30 --batch-size 5 \
  --repository ./repository-HANDLE --quality best \
  --auth-browser firefox --auth-profile PROFILE_NAME
uv run xma status --repository ./repository-HANDLE --json
```

`PROVIDER_EXHAUSTED` is the only full-account completion terminal. A safety cap pauses resumably;
timeouts, transport failures and worker failures do not imply exhaustion. Back up the complete
repository before any governed reconciliation.

## Repository layout

```text
repository-HANDLE/
├── catalog.sqlite3
├── manifests/latest.json
└── profiles/HANDLE/posts/POST_ID/MEDIA_INDEX/
    ├── metadata.json
    └── video.EXT
```

The video is always named `video` plus its validated media extension. The adjacent
`metadata.json` is its sidecar. Back up the complete repository; do not move or edit individual
cataloged files.

## Limits and common errors

- Linux x86_64 only; Ubuntu 22.04 and 24.04 are tested.
- Download accepts `--limit 1..10` or `--add 1..20`, never both; the resulting repository total
  cannot exceed twenty; additive requests accept 1..20. BOUNDED archive is capped at twenty, while
  ALL requires an explicit operational cap and is not a mass-download certification.
- No scheduler, daemon, mass operation, remote cursor, GUI, API service, yt-dlp, or FFmpeg.
- `archive --all` uses `RESCAN_DEDUP_V2`; it is validated for one observed account, not thousands
  of downloads or every X account.
- Exit `2`: invalid input; `3`: authentication/content restriction; `4`: rate limit; `5`:
  provider/contract failure; `6`: catalog failure; `7`: missing target/run; `8`: transient provider
  failure/timeout; `9`: download or repository conflict.
- Provider timeout or rate limiting is not permission for unbounded retry. Preserve the repository
  and inspect `status` offline.
- Stop on catalog/filesystem/hash disagreement. Never delete the catalog to force recovery.

See `README.md` and `docs/operations/` inside this bundle for integrity, backup, troubleshooting,
and rollback procedures.

## Reading command results

Human output is compact: a single newly downloaded video includes public media metadata, SHA-256,
size, and its repository-relative file path; two or more downloads show aggregate counts. A no-op
states that no new video was downloaded. Add `--json` for automation: legacy fields remain and the
new additive `report` object has schema version 1. On failure, JSON is written only to stderr and
contains a stable error code, preserved progress when available, checkpoint, and resumability.
