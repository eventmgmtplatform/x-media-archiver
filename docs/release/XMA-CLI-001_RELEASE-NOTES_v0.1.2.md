# X Media Archiver v0.1.2 release notes

**Status:** release candidate; not yet tagged or published.

Version 0.1.2 strengthens bounded media recovery while keeping XMA local-first and explicitly
non-bulk. Interactive absolute download remains 1–10; additive download accepts 1–20 with a hard
verified repository maximum of twenty. Durable archive is also capped at twenty.

## Included

- Constant sanitized HTTP/media classifications without raw provider or signed-URL disclosure.
- One bounded internal URL renewal path and at most two configured discovery attempts.
- Continued scanning after a failed media candidate, with command-local failed-identity exclusion.
- An active discovery deadline that excludes consumer transfer/persistence time.
- Pending IPC drain before timeout classification, with terminate/kill/join cleanup preserved.
- Provider-best quality metadata and an opt-in public acceptance harness using the local CLI.
- Controlled public evidence completing 0→5→10→20 with intact prior hashes and no staging residue.

## Validation observation

The public acceptance did not produce a DownloadError. Continuation after a failed media candidate
is validated by deterministic offline tests; it is not claimed as publicly observed behavior.

## Distribution

The candidate contains a Linux x86_64 standalone bundle, wheel, source distribution, CycloneDX
SBOM, locked production requirements, complete GPL-2.0-only license text, third-party notices,
sanitized release manifest, checksums, and the verified official corresponding source archive for
gallery-dl 1.32.18.

## Limits

- Linux x86_64; Ubuntu 22.04 and 24.04 are the candidate portability targets.
- No mass-download certification, scheduler, daemon, remote durable cursor, PyPI publication, or
  operation above twenty.
- Provider availability and authenticated X behavior remain external dependencies.

Publishing v0.1.2 requires a separate human decision. This candidate preparation does not create a
tag, GitHub Release, or PyPI publication.
