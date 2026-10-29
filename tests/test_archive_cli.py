"""Offline B05 archive and status CLI tests."""

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xma.cli as cli
from xma.cli import app
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.download import DownloadedArtifact
from xma.domain.enums import MediaType, PostType

runner = CliRunner()
NOW = datetime(2026, 10, 29, tzinfo=UTC)


class Incremental:
    def candidates(
        self,
        target: DiscoveryTarget,
        remaining: int,
        existing_identities: frozenset[str],
        timeout_seconds: int,
        max_scan: int = 100,
    ) -> Iterator[DiscoveryBatch]:
        del timeout_seconds, max_scan
        start = len(existing_identities)
        for index in range(start, start + remaining):
            post_id = str(9000 + index)
            asset = DiscoveredAsset(
                post_id,
                0,
                MediaType.VIDEO,
                1000,
                1280,
                720,
                (f"https://media.invalid/{index}?secret=fixture",),
            )
            yield DiscoveryBatch(
                target,
                "fixture:archive",
                DiscoveredProfile("123", target.handle, target.handle),
                (DiscoveredPost(post_id, "123", "fixture", NOW, PostType.POST, (asset,)),),
                NOW,
                1,
            )


class Media:
    def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
        payload = hashlib.sha256(source_url.encode()).digest()
        Path(part_path).write_bytes(payload)
        return DownloadedArtifact(
            "video/mp4", len(payload), hashlib.sha256(payload).hexdigest(), ".mp4"
        )


def test_archive_and_status_json_are_stable_and_offline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", lambda: object())
    monkeypatch.setattr(cli, "_media_provider_factory", Media)
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())
    monkeypatch.setattr("xma.application.archive.time.sleep", lambda seconds: None)
    repository = tmp_path / "repository"

    archived = runner.invoke(
        app,
        [
            "archive",
            "BBCWorld",
            "--limit",
            "2",
            "--batch-size",
            "1",
            "--request-interval",
            "1",
            "--repository",
            str(repository),
            "--json",
        ],
    )
    assert archived.exit_code == 0, archived.stderr
    payload = json.loads(archived.stdout)
    assert payload["status"] == "COMPLETED"
    assert payload["downloaded_total"] == 2
    assert payload["remaining"] == 0
    assert "secret=fixture" not in archived.stdout

    status = runner.invoke(app, ["status", "--repository", str(repository), "--json"])
    assert status.exit_code == 0
    assert json.loads(status.stdout) == payload
    human = runner.invoke(app, ["status", "--repository", str(repository)])
    assert human.exit_code == 0
    assert "status: COMPLETED" in human.stdout
    assert "checkpoint_strategy: RESCAN_DEDUP_V1" in human.stdout


def test_status_without_run_is_read_only(tmp_path: Path) -> None:
    repository = tmp_path / "missing"
    result = runner.invoke(app, ["status", "--repository", str(repository), "--json"])
    assert result.exit_code == cli.EXIT_NOT_FOUND
    assert "no durable run" in result.stderr
    assert not repository.exists()


@pytest.mark.parametrize(
    "arguments",
    [
        ["--limit", "0"],
        ["--limit", "21"],
        ["--batch-size", "0"],
        ["--batch-size", "6"],
        ["--request-interval", "0"],
        ["--request-interval", "61"],
    ],
)
def test_archive_cli_rejects_out_of_range_options(arguments: list[str]) -> None:
    result = runner.invoke(app, ["archive", "BBCWorld", *arguments])
    assert result.exit_code == cli.EXIT_INVALID_INPUT


def test_archive_cli_rejects_single_post(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "archive",
            "https://x.com/BBCWorld/status/123",
            "--repository",
            str(tmp_path / "repository"),
        ],
    )
    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert not (tmp_path / "repository").exists()
