#!/usr/bin/env python3
"""Generate or validate the sanitized v0.2.0 release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
VERSION = "0.2.0"
EXPECTED_TAG = f"v{VERSION}"
MANIFEST_NAME = "RELEASE-MANIFEST.json"
CHECKSUM_NAME = "SHA256SUMS"
CONTROL_ASSETS = (
    {
        "name": MANIFEST_NAME,
        "role": "manifest",
        "digest_policy": "verified-by-SHA256SUMS",
    },
    {
        "name": CHECKSUM_NAME,
        "role": "checksum-index",
        "digest_policy": "external-release-asset-digest",
    },
)
RELEASE_ASSET_NAMES = (*PAYLOADS, MANIFEST_NAME, CHECKSUM_NAME)
TAG_PATTERN = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), text=True).strip()


def release_tag() -> str:
    explicit = os.environ.get("RELEASE_TAG")
    if explicit:
        tag = explicit
    elif os.environ.get("GITHUB_REF_TYPE") == "tag":
        tag = os.environ.get("GITHUB_REF_NAME", "")
    else:
        raise SystemExit("release tag is required")
    if not TAG_PATTERN.fullmatch(tag):
        raise SystemExit("release tag format is invalid")
    if tag != EXPECTED_TAG:
        raise SystemExit("release tag/version mismatch")
    return tag


def release_assets() -> list[dict[str, str]]:
    payloads = [{"name": name, "role": "payload"} for name in PAYLOADS]
    return [*payloads, *CONTROL_ASSETS]


def validate_release_notes(path: Path) -> None:
    expected_name = f"XMA-CLI-001_RELEASE-NOTES_v{VERSION}.md"
    if path.name != expected_name:
        raise SystemExit("release notes version mismatch")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit("release notes are empty")
    if f"v{VERSION}" not in text.splitlines()[0]:
        raise SystemExit("release notes heading mismatch")


def checksum_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != 9:
        raise SystemExit("SHA256SUMS must contain exactly nine entries")
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise SystemExit("SHA256SUMS entry is invalid")
        name = parts[1].lstrip("* ")
        if name in entries:
            raise SystemExit("SHA256SUMS contains duplicate entries")
        entries[name] = parts[0]
    expected = {*PAYLOADS, MANIFEST_NAME}
    if set(entries) != expected or CHECKSUM_NAME in entries:
        raise SystemExit("SHA256SUMS inventory mismatch")
    return entries


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
        "version": VERSION,
        "tag": release_tag(),
        "supported_platform": "Linux x86_64 (Ubuntu 22.04 and 24.04)",
        "minimum_python": "3.11",
        "entry_point": "xma",
        "gallery_dl_version": "1.32.18",
        "license": "GPL-2.0-only",
        "source_date_epoch": int(os.environ.get("SOURCE_DATE_EPOCH", "1793246400")),
        "verification": "sha256sum -c SHA256SUMS",
        "source_sha": source_sha,
        "source_tree": source_tree,
        "uv_lock_sha256": sha256(Path("uv.lock")),
        "release_asset_count": 10,
        "payload_asset_count": 8,
        "control_asset_count": 2,
        "release_assets": release_assets(),
        "bundle": {
            "name": "xma-v0.2.0-linux-x86_64.tar.gz",
            "format": "tar+gzip",
            "layout": "xma-v0.2.0-linux-x86_64/",
        },
        "artifacts": artifacts,
    }


def validate(artifact_dir: Path) -> None:
    manifest_path = artifact_dir / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text())
    if manifest["schema"] != "xma-release-manifest-v1" or manifest["version"] != VERSION:
        raise SystemExit("release manifest schema/version mismatch")
    if manifest.get("tag") != release_tag():
        raise SystemExit("release manifest tag mismatch")
    expected_sha = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD")
    if manifest["source_sha"] != expected_sha:
        raise SystemExit("release manifest source SHA mismatch")
    if manifest["source_tree"] != git("rev-parse", f"{expected_sha}^{{tree}}"):
        raise SystemExit("release manifest source tree mismatch")
    if manifest["uv_lock_sha256"] != sha256(Path("uv.lock")):
        raise SystemExit("release manifest uv.lock mismatch")
    entries = {item["name"]: item for item in manifest["artifacts"]}
    if len(entries) != len(manifest["artifacts"]):
        raise SystemExit("release manifest contains duplicate payloads")
    if set(entries) != set(PAYLOADS):
        raise SystemExit("release manifest artifact inventory mismatch")
    for name in PAYLOADS:
        path = artifact_dir / name
        if entries[name]["size"] != path.stat().st_size or entries[name]["sha256"] != sha256(path):
            raise SystemExit(f"release manifest artifact mismatch: {name}")
    expected_assets = release_assets()
    if manifest.get("release_assets") != expected_assets:
        raise SystemExit("release manifest release asset inventory mismatch")
    if (
        manifest.get("release_asset_count") != 10
        or manifest.get("payload_asset_count") != 8
        or manifest.get("control_asset_count") != 2
    ):
        raise SystemExit("release manifest asset counts mismatch")
    for control in manifest["release_assets"][-2:]:
        if "sha256" in control or "size" in control:
            raise SystemExit("control assets must not contain self-referential digests")
    checksums = checksum_entries(artifact_dir / CHECKSUM_NAME)
    for name, expected_digest in checksums.items():
        if sha256(artifact_dir / name) != expected_digest:
            raise SystemExit(f"SHA256SUMS digest mismatch: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--validate-release-notes", type=Path)
    parser.add_argument("artifact_dir", type=Path, nargs="?")
    args = parser.parse_args()
    if args.validate_release_notes is not None:
        validate_release_notes(args.validate_release_notes)
        return
    if args.artifact_dir is None:
        parser.error("artifact_dir is required")
    if args.validate:
        validate(args.artifact_dir)
        return
    manifest = build_manifest(args.artifact_dir)
    output = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (args.artifact_dir / "RELEASE-MANIFEST.json").write_text(output)


if __name__ == "__main__":
    main()
