# XMA-CLI-001 release checklist v1.0.0

- [ ] Release branch created from current protected main; scope frozen.
- [ ] Version, changelog, README, requirements and BAU documentation reconciled.
- [ ] License, third-party notices and corresponding-source checksum reviewed.
- [ ] Ruff, mypy, full pytest and coverage ≥90% pass.
- [ ] Dependency vulnerability and secret scans pass; license inventory reviewed.
- [ ] Wheel/sdist contents inspected; isolated wheel install passes.
- [ ] Linux bundle built on Ubuntu 22.04 and validated on 22.04 and 24.04 without Python/uv in PATH.
- [ ] Help/version/subcommand helps and synthetic offline status pass.
- [ ] SBOM, requirements and SHA256SUMS present and verified.
- [ ] Draft PR CI green; handoff reviewed; human approval recorded.
- [ ] Squash merge performed by authorized human.
- [ ] Annotated tag created from main without rewriting history.
- [ ] Manual workflow creates draft GitHub Release; artifacts and notes reviewed before publish.
- [ ] Postrelease checksum, extraction and offline smoke pass.
- [ ] Rollback/patch plan and support notification are ready.
