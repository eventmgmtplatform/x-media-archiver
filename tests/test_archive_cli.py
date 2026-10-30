"""Offline B05 archive and status CLI tests."""

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xma.cli as cli
from xma.adapters.archive import SQLiteArchiveStore
from xma.cli import app
from xma.domain.archive import ArchiveStatus
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
    status_payload = json.loads(status.stdout)
    assert {key: value for key, value in status_payload.items() if key != "report"} == {
        key: value for key, value in payload.items() if key != "report"
    }
    assert payload["report"]["command"] == "archive"
    assert status_payload["report"]["command"] == "status"
    human = runner.invoke(app, ["status", "--repository", str(repository)])
    assert human.exit_code == 0
    assert "status: COMPLETED" in human.stdout
    assert "checkpoint_strategy: RESCAN_DEDUP_V2" in human.stdout


def test_status_without_run_is_read_only(tmp_path: Path) -> None:
    repository = tmp_path / "missing"
    result = runner.invoke(app, ["status", "--repository", str(repository), "--json"])
    assert result.exit_code == cli.EXIT_NOT_FOUND
    error = json.loads(result.stderr)
    assert result.stdout == ""
    assert error["error_code"] == "NOT_FOUND"
    assert error["progress_available"] is False
    assert not repository.exists()


def test_archive_all_safety_cap_and_status_are_offline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", lambda: object())
    monkeypatch.setattr(cli, "_media_provider_factory", Media)
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())
    monkeypatch.setattr("xma.application.archive.time.sleep", lambda seconds: None)
    repository = tmp_path / "repository"
    result = runner.invoke(
        app,
        [
            "archive",
            "BBCWorld",
            "--all",
            "--max-items",
            "2",
            "--batch-size",
            "1",
            "--request-interval",
            "1",
            "--min-free-space-gib",
            "5",
            "--repository",
            str(repository),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "ALL"
    assert payload["status"] == "PAUSED"
    assert payload["completion_reason"] == "SAFETY_CAP_REACHED"
    assert payload["verified_total"] == 2
    assert payload["resumable"] is True
    assert payload["requested_total"] is None
    assert payload["remaining"] is None
    assert payload["goal"] == "PROVIDER_EXHAUSTION"
    assert payload["operational_cap"] == 2
    assert payload["complete"] is False


def test_archive_cli_sanitizes_unexpected_service_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    marker = "SECRET_TOKEN path=/private signed=https://media.invalid/?token=raw"

    def fail(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError(marker)

    monkeypatch.setattr(cli, "_provider_factory", lambda: object())
    monkeypatch.setattr(cli, "_media_provider_factory", Media)
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())
    monkeypatch.setattr("xma.application.download.DownloadService.execute_incremental", fail)
    repository = tmp_path / "repository"
    result = runner.invoke(
        app,
        [
            "archive",
            "BBCWorld",
            "--all",
            "--max-items",
            "1",
            "--min-free-space-gib",
            "5",
            "--repository",
            str(repository),
            "--json",
        ],
    )
    output = result.stdout + result.stderr
    assert result.exit_code == cli.EXIT_PROVIDER_FAILED
    error = json.loads(result.stderr)
    assert result.stdout == ""
    assert error["error_code"] == "UNEXPECTED_FAILURE"
    assert error["status"] == "FAILED"
    assert marker not in output
    assert "Traceback" not in output
    restored = SQLiteArchiveStore(repository / "catalog.sqlite3").latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.FAILED
    assert restored.last_error_code == "UNEXPECTED_FAILURE"


@pytest.mark.parametrize(
    "arguments",
    [
        ["--all", "--limit", "1"],
        ["--max-items", "5"],
        ["--resume"],
        ["--all", "--quality", "worst"],
    ],
)
def test_archive_all_invalid_combinations_fail_before_repository(
    arguments: list[str], tmp_path: Path
) -> None:
    repository = tmp_path / "repository"
    result = runner.invoke(
        app, ["archive", "BBCWorld", *arguments, "--repository", str(repository)]
    )
    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert not repository.exists()


@pytest.mark.parametrize(
    "arguments",
    [
        ["--limit", "0"],
        ["--limit", "21"],
        ["--batch-size", "0"],
        ["--batch-size", "21"],
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
