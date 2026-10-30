#!/usr/bin/env python3
"""Generate or validate the sanitized v0.2.0 release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path

PAYLOADS = (
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "gallery_dl-1.32.18.tar.gz",
    "requirements-linux-x86_64.txt",
    "sbom.cdx.json",
    "x_media_archiver-0.2.0-py3-none-any.whl",
    "x_media_archiver-0.2.0.tar.gz",
    "xma-v0.2.0-linux-x86_64.tar.gz",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), text=True).strip()


def build_manifest(artifact_dir: Path) -> dict[str, object]:
    source_sha = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD")
    source_tree = git("rev-parse", f"{source_sha}^{{tree}}")
    artifacts = []
    for name in PAYLOADS:
        path = artifact_dir / name
        artifacts.append({"name": name, "size": path.stat().st_size, "sha256": sha256(path)})
    return {
        "schema": "xma-release-manifest-v1",
        "product": "X Media Archiver",
        "version": "0.2.0",
        "supported_platform": "Linux x86_64 (Ubuntu 22.04 and 24.04)",
        "minimum_python": "3.12",
        "entry_point": "xma",
        "gallery_dl_version": "1.32.18",
        "license": "GPL-2.0-only",
        "source_date_epoch": int(os.environ.get("SOURCE_DATE_EPOCH", "1793246400")),
        "verification": "sha256sum -c SHA256SUMS",
        "source_sha": source_sha,
        "source_tree": source_tree,
        "uv_lock_sha256": sha256(Path("uv.lock")),
        "build": {"python": platform.python_version(), "platform": platform.platform()},
        "bundle": {
            "name": "xma-v0.2.0-linux-x86_64.tar.gz",
            "format": "tar+gzip",
            "layout": "xma-v0.2.0-linux-x86_64/",
        },
        "artifacts": artifacts,
    }


def validate(artifact_dir: Path) -> None:
    manifest = json.loads((artifact_dir / "RELEASE-MANIFEST.json").read_text())
    if manifest["schema"] != "xma-release-manifest-v1" or manifest["version"] != "0.2.0":
        raise SystemExit("release manifest schema/version mismatch")
    expected_sha = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD")
    if manifest["source_sha"] != expected_sha:
        raise SystemExit("release manifest source SHA mismatch")
    if manifest["source_tree"] != git("rev-parse", f"{expected_sha}^{{tree}}"):
        raise SystemExit("release manifest source tree mismatch")
    if manifest["uv_lock_sha256"] != sha256(Path("uv.lock")):
        raise SystemExit("release manifest uv.lock mismatch")
    entries = {item["name"]: item for item in manifest["artifacts"]}
    if set(entries) != set(PAYLOADS):
        raise SystemExit("release manifest artifact inventory mismatch")
    for name in PAYLOADS:
        path = artifact_dir / name
        if entries[name]["size"] != path.stat().st_size or entries[name]["sha256"] != sha256(path):
            raise SystemExit(f"release manifest artifact mismatch: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("artifact_dir", type=Path)
    args = parser.parse_args()
    if args.validate:
        validate(args.artifact_dir)
        return
    manifest = build_manifest(args.artifact_dir)
    output = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (args.artifact_dir / "RELEASE-MANIFEST.json").write_text(output)


if __name__ == "__main__":
    main()
