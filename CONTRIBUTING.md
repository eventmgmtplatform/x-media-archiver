# Contributing

Open an issue before broad changes. Branch from current main, keep scope small, use Conventional
Commits and add offline tests. Run `uv sync --locked --all-groups`, Ruff format/lint, mypy, pytest,
build and `git diff --check`. Never commit secrets, cookies, media, SQLite or release artifacts.
All changes use a PR; releases require the governed checklist and human approval.
