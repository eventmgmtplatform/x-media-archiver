# X Media Archiver v0.1.1 draft release notes

This bounded hotfix repairs retry/reconciliation after a final media-download failure, makes lower
absolute limits offline idempotent, adds `download --add`, bounds scanning, and records the explicit
`provider-best` quality policy.

Interactive download accepts absolute totals 1–10 or additive requests 1–10 when the resulting
verified repository total remains at most ten. Invalid totals stop before provider, authentication,
network or repository creation and direct larger future work to durable `xma archive`. Archive is
also capped at ten in v0.1.1.

There is no mass-download, scheduler, unattended-operation, transcoding, yt-dlp or FFmpeg support.
Publication still requires a separate human merge/tag/release decision.

Governed validation completed 391 offline tests at 90.63% coverage and the single authorized public
acceptance sequence 0→1→2→5. A subsequent absolute limit 1 was an offline no-op that preserved all
five verified artifacts. This evidence does not authorize publication or operation above ten.
