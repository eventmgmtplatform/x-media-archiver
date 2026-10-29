from __future__ import annotations

import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = "0.1.0"

project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
init_text = (ROOT / "src/xma/__init__.py").read_text(encoding="utf-8")
match = re.search(r'^__version__ = "([^"]+)"$', init_text, re.MULTILINE)
if project["version"] != EXPECTED or match is None or match.group(1) != EXPECTED:
    raise SystemExit("release version metadata is inconsistent")

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if changelog.count("## [Unreleased]") != 1 or "## [0.1.0] - 2026-10-29" not in changelog:
    raise SystemExit("changelog release sections are inconsistent")

for forbidden in ("*.sqlite3", "cookies.sqlite", "*.mp4", "release-artifacts/"):
    if forbidden not in (ROOT / ".gitignore").read_text(encoding="utf-8"):
        raise SystemExit(f"missing ignore rule: {forbidden}")

sys.stdout.write("release metadata: PASS\n")
