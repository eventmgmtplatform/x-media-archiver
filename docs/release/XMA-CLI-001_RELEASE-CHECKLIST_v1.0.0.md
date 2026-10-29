# XMA-CLI-001 release checklist v1.0.0

- [x] Release branch created from current protected main; scope frozen.
- [x] Version, changelog, README, requirements and BAU documentation reconciled.
- [x] License, third-party notices and corresponding-source checksum reviewed.
- [x] Ruff, mypy, full pytest and coverage ≥90% pass.
- [x] Dependency vulnerability and secret scans pass; license inventory reviewed.
- [x] Wheel/sdist contents inspected; isolated wheel install passes.
- [x] Linux bundle built on Ubuntu 22.04 and validated on 22.04 and 24.04 without Python/uv in PATH.
- [x] Help/version/subcommand helps and synthetic offline status pass.
- [x] SBOM, requirements and SHA256SUMS present and verified.
- [x] Draft PR CI green; handoff reviewed; human approval recorded.
- [x] Squash merge performed by authorized human.
- [x] Annotated tag created from main without rewriting history.
- [x] Manual workflow creates draft GitHub Release; artifacts and notes reviewed before publish.
- [x] Postrelease checksum, extraction and offline smoke pass.
- [x] Rollback/patch plan and support notification are ready.
