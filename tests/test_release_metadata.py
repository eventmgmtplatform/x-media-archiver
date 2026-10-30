from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest


def load_module() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "generate-release-manifest.py"
    spec = importlib.util.spec_from_file_location("release_manifest", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def manifest_module() -> ModuleType:
    return load_module()


@pytest.fixture
def artifact_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType
) -> Path:
    monkeypatch.setenv("RELEASE_TAG", "v0.2.0")
    directory = tmp_path / "assets"
    directory.mkdir()
    for index, name in enumerate(manifest_module.PAYLOADS):
        (directory / name).write_bytes(f"payload-{index}".encode())
    manifest = manifest_module.build_manifest(directory)
    (directory / manifest_module.MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksum_names = (*manifest_module.PAYLOADS, manifest_module.MANIFEST_NAME)
    checksums = "".join(
        f"{manifest_module.sha256(directory / name)}  {name}\n" for name in checksum_names
    )
    (directory / manifest_module.CHECKSUM_NAME).write_text(checksums, encoding="utf-8")
    return directory


def read_manifest(directory: Path) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads((directory / "RELEASE-MANIFEST.json").read_text(encoding="utf-8")),
    )


def write_manifest(directory: Path, manifest: dict[str, Any]) -> None:
    (directory / "RELEASE-MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def refresh_manifest_checksum(directory: Path, module: ModuleType) -> None:
    lines = (directory / module.CHECKSUM_NAME).read_text(encoding="utf-8").splitlines()
    updated = []
    for line in lines:
        name = line.split(maxsplit=1)[1]
        digest = module.sha256(directory / name)
        updated.append(f"{digest}  {name}")
    (directory / module.CHECKSUM_NAME).write_text("\n".join(updated) + "\n", encoding="utf-8")


def test_release_tag_explicit(monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType) -> None:
    monkeypatch.setenv("RELEASE_TAG", "v0.2.0")
    assert manifest_module.release_tag() == "v0.2.0"


def test_release_tag_from_github_tag(
    monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType
) -> None:
    monkeypatch.delenv("RELEASE_TAG", raising=False)
    monkeypatch.setenv("GITHUB_REF_TYPE", "tag")
    monkeypatch.setenv("GITHUB_REF_NAME", "v0.2.0")
    assert manifest_module.release_tag() == "v0.2.0"


def test_release_tag_missing(monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType) -> None:
    monkeypatch.delenv("RELEASE_TAG", raising=False)
    monkeypatch.delenv("GITHUB_REF_TYPE", raising=False)
    with pytest.raises(SystemExit, match="required"):
        manifest_module.release_tag()


def test_branch_ref_rejected(monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType) -> None:
    monkeypatch.delenv("RELEASE_TAG", raising=False)
    monkeypatch.setenv("GITHUB_REF_TYPE", "branch")
    monkeypatch.setenv("GITHUB_REF_NAME", "v0.2.0")
    with pytest.raises(SystemExit, match="required"):
        manifest_module.release_tag()


def test_tag_version_mismatch(monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType) -> None:
    monkeypatch.setenv("RELEASE_TAG", "v0.1.2")
    with pytest.raises(SystemExit, match="mismatch"):
        manifest_module.release_tag()


def test_tag_format_rejected(monkeypatch: pytest.MonkeyPatch, manifest_module: ModuleType) -> None:
    monkeypatch.setenv("RELEASE_TAG", "refs/heads/main")
    with pytest.raises(SystemExit, match="format"):
        manifest_module.release_tag()


def test_inventory_contract_10_8_2(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    assert manifest["tag"] == "v0.2.0"
    assert manifest["release_asset_count"] == 10
    assert manifest["payload_asset_count"] == 8
    assert manifest["control_asset_count"] == 2
    assert len(manifest["release_assets"]) == 10
    manifest_module.validate(artifact_dir)


@pytest.mark.parametrize("missing", ["LICENSE", "x_media_archiver-0.2.0.tar.gz"])
def test_missing_payload_rejected(
    artifact_dir: Path, manifest_module: ModuleType, missing: str
) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["artifacts"] = [item for item in manifest["artifacts"] if item["name"] != missing]
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="artifact inventory"):
        manifest_module.validate(artifact_dir)


def test_additional_payload_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["artifacts"].append({"name": "extra.bin", "size": 1, "sha256": "0" * 64})
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="artifact inventory"):
        manifest_module.validate(artifact_dir)


def test_duplicate_payload_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["artifacts"].append(manifest["artifacts"][0])
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="duplicate payloads"):
        manifest_module.validate(artifact_dir)


def test_missing_control_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["release_assets"] = manifest["release_assets"][:-1]
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="release asset inventory"):
        manifest_module.validate(artifact_dir)


def test_duplicate_control_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["release_assets"][-1] = manifest["release_assets"][-2]
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="release asset inventory"):
        manifest_module.validate(artifact_dir)


def test_payload_hash_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["artifacts"][0]["sha256"] = "0" * 64
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="artifact mismatch"):
        manifest_module.validate(artifact_dir)


def test_payload_size_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    manifest = read_manifest(artifact_dir)
    manifest["artifacts"][0]["size"] = -1
    write_manifest(artifact_dir, manifest)
    refresh_manifest_checksum(artifact_dir, manifest_module)
    with pytest.raises(SystemExit, match="artifact mismatch"):
        manifest_module.validate(artifact_dir)


def test_manifest_is_in_checksums(artifact_dir: Path, manifest_module: ModuleType) -> None:
    entries = manifest_module.checksum_entries(artifact_dir / manifest_module.CHECKSUM_NAME)
    assert manifest_module.MANIFEST_NAME in entries


def test_checksums_exclude_themselves(artifact_dir: Path, manifest_module: ModuleType) -> None:
    entries = manifest_module.checksum_entries(artifact_dir / manifest_module.CHECKSUM_NAME)
    assert manifest_module.CHECKSUM_NAME not in entries
    assert len(entries) == 9


def test_checksum_duplicate_rejected(artifact_dir: Path, manifest_module: ModuleType) -> None:
    path = artifact_dir / manifest_module.CHECKSUM_NAME
    first = path.read_text(encoding="utf-8").splitlines()[0]
    path.write_text(path.read_text(encoding="utf-8") + first + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="exactly nine"):
        manifest_module.checksum_entries(path)


def test_no_self_referential_control_digests(
    artifact_dir: Path, manifest_module: ModuleType
) -> None:
    controls = read_manifest(artifact_dir)["release_assets"][-2:]
    assert all("sha256" not in item and "size" not in item for item in controls)


def test_release_notes_v020(tmp_path: Path, manifest_module: ModuleType) -> None:
    path = tmp_path / "XMA-CLI-001_RELEASE-NOTES_v0.2.0.md"
    path.write_text("# X Media Archiver v0.2.0 release notes\n", encoding="utf-8")
    manifest_module.validate_release_notes(path)


def test_release_notes_v012_rejected(tmp_path: Path, manifest_module: ModuleType) -> None:
    path = tmp_path / "XMA-CLI-001_RELEASE-NOTES_v0.1.2.md"
    path.write_text("# X Media Archiver v0.1.2 release notes\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="version mismatch"):
        manifest_module.validate_release_notes(path)


def test_release_notes_empty_rejected(tmp_path: Path, manifest_module: ModuleType) -> None:
    path = tmp_path / "XMA-CLI-001_RELEASE-NOTES_v0.2.0.md"
    path.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="empty"):
        manifest_module.validate_release_notes(path)


def test_release_workflow_selects_v020_notes() -> None:
    root = Path(__file__).parents[1]
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "XMA-CLI-001_RELEASE-NOTES_v0.2.0.md" in workflow
    assert "XMA-CLI-001_RELEASE-NOTES_v0.1.2.md" not in workflow
    assert "RELEASE_TAG: ${{ inputs.tag }}" in workflow


def test_checksum_generation_order_is_non_circular() -> None:
    root = Path(__file__).parents[1]
    script = (root / "scripts" / "build-release-candidate.sh").read_text(encoding="utf-8")
    checksum_inputs = script.split("sha256sum LICENSE", maxsplit=1)[1].split(
        "> SHA256SUMS", maxsplit=1
    )[0]
    assert "RELEASE-MANIFEST.json" in checksum_inputs
    assert "SHA256SUMS" not in checksum_inputs


def test_manifest_has_no_personal_paths(artifact_dir: Path) -> None:
    text = (artifact_dir / "RELEASE-MANIFEST.json").read_text(encoding="utf-8")
    assert "/home/" not in text
    assert "cookies" not in text.lower()
