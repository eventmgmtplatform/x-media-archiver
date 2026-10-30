"""CLI tests for the bounded B04 download command."""

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xma.cli as cli
from xma.application.download import DownloadService
from xma.cli import app
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.download import DownloadedArtifact, DownloadSummary
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import DiscoveryTransientError

runner = CliRunner()
NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


class Discovery:
    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        post = DiscoveredPost(
            "9001",
            "123",
            "report",
            NOW,
            PostType.POST,
            (
                DiscoveredAsset(
                    "9001",
                    0,
                    MediaType.VIDEO,
                    1000,
                    1280,
                    720,
                    ("https://media.invalid/video.mp4?private=signature",),
                ),
            ),
        )
        return DiscoveryBatch(
            target,
            "fixture:download",
            DiscoveredProfile("123", target.handle, "Reuters"),
            (post,),
            NOW,
            limit,
        )


class Media:
    def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
        payload = b"synthetic-video"
        Path(part_path).write_bytes(payload)
        return DownloadedArtifact(
            "video/mp4",
            len(payload),
            hashlib.sha256(payload).hexdigest(),
            ".mp4",
        )


class Incremental:
    def candidates(
        self,
        target: DiscoveryTarget,
        remaining: int,
        existing_identities: frozenset[str],
        timeout_seconds: int,
        max_scan: int = 100,
    ) -> Iterator[DiscoveryBatch]:
        del existing_identities, timeout_seconds, max_scan
        yield Discovery().discover(target, remaining)


def test_download_json_is_stable_and_omits_ephemeral_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", Discovery)
    monkeypatch.setattr(cli, "_media_provider_factory", Media)
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())
    repository = tmp_path / "repository"

    result = runner.invoke(
        app,
        [
            "download",
            "Reuters",
            "--limit",
            "1",
            "--repository",
            str(repository),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["downloaded_count"] == 1
    assert payload["skipped_count"] == 0
    assert payload["requested_limit"] == 1
    assert "private=signature" not in result.stdout
    assert (repository / "catalog.sqlite3").is_file()


@pytest.mark.parametrize("limit", ["0", "11", "1000"])
def test_download_cli_rejects_limit_outside_one_to_ten(limit: str) -> None:
    result = runner.invoke(app, ["download", "Reuters", "--limit", limit])
    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert "between 1 and 10" in result.stderr


@pytest.mark.parametrize("limit", range(1, 11))
def test_download_cli_accepts_every_limit_one_to_ten(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, limit: int
) -> None:
    monkeypatch.setattr(DownloadService, "verified_total", lambda self, handle: 10)
    monkeypatch.setattr(
        DownloadService,
        "execute_incremental",
        lambda self, request, *args: DownloadSummary(
            request.target, request.limit, 0, 10, 0, "run", (), 10, 10, True
        ),
    )
    result = runner.invoke(
        app,
        ["download", "Reuters", "--limit", str(limit), "--repository", str(tmp_path / "repo")],
    )
    assert result.exit_code == 0


@pytest.mark.parametrize("additional", [1, 2, 3, 5, 10, 20])
def test_download_cli_accepts_every_add_value(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, additional: int
) -> None:
    captured: list[int] = []
    monkeypatch.setattr(DownloadService, "verified_total", lambda self, handle: 0)

    def execute(self: DownloadService, request: object, *args: object) -> DownloadSummary:
        captured.append(request.limit)  # type: ignore[attr-defined]
        return DownloadSummary("https://x.com/Reuters", additional, 0, 0, 0, "run", (), 0, 0, True)

    monkeypatch.setattr(DownloadService, "execute_incremental", execute)
    monkeypatch.setattr(cli, "_download_discovery_provider", lambda *args: Discovery())
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())
    result = runner.invoke(
        app,
        ["download", "Reuters", "--add", str(additional), "--repository", str(tmp_path / "repo")],
    )
    assert result.exit_code == 0
    assert captured == [additional]


@pytest.mark.parametrize(("existing", "additional"), [(5, 5), (0, 10), (0, 20)])
def test_download_cli_additive_total_is_absolute_target(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, existing: int, additional: int
) -> None:
    captured: list[int] = []
    monkeypatch.setattr(DownloadService, "verified_total", lambda self, handle: existing)
    monkeypatch.setattr(cli, "_download_discovery_provider", lambda *args: Discovery())
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())

    def execute(self: DownloadService, request: object, *args: object) -> DownloadSummary:
        captured.append(request.limit)  # type: ignore[attr-defined]
        return DownloadSummary(
            "https://x.com/Reuters",
            existing + additional,
            0,
            existing,
            0,
            "run",
            (),
            existing,
            existing,
            True,
        )

    monkeypatch.setattr(DownloadService, "execute_incremental", execute)
    result = runner.invoke(
        app,
        ["download", "Reuters", "--add", str(additional), "--repository", str(tmp_path / "repo")],
    )
    assert result.exit_code == 0
    assert captured == [existing + additional]


@pytest.mark.parametrize(("existing", "additional"), [(5, 16), (20, 1)])
def test_download_cli_rejects_additive_total_above_twenty_before_provider_or_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    existing: int,
    additional: int,
) -> None:
    repository = tmp_path / "must-not-exist"
    monkeypatch.setattr(DownloadService, "verified_total", lambda self, handle: existing)
    monkeypatch.setattr(
        cli,
        "_download_discovery_provider",
        lambda *args: pytest.fail("provider must not be constructed"),
    )
    result = runner.invoke(
        app,
        ["download", "Reuters", "--add", str(additional), "--repository", str(repository)],
    )
    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert "must not exceed 20" in result.stderr
    assert not repository.exists()


def test_download_cli_rejects_limit_and_add_together(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["download", "Reuters", "--limit", "1", "--add", "1", "--repository", str(tmp_path)],
    )
    assert result.exit_code == cli.EXIT_INVALID_INPUT


def test_download_cli_default_remains_limit_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: list[int] = []
    monkeypatch.setattr(DownloadService, "verified_total", lambda self, handle: 0)
    monkeypatch.setattr(cli, "_download_discovery_provider", lambda *args: Discovery())
    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: Incremental())

    def execute(self: DownloadService, request: object, *args: object) -> DownloadSummary:
        captured.append(request.limit)  # type: ignore[attr-defined]
        return DownloadSummary("https://x.com/Reuters", 1, 0, 0, 0, "run", (), 0, 0, True)

    monkeypatch.setattr(DownloadService, "execute_incremental", execute)
    result = runner.invoke(app, ["download", "Reuters", "--repository", str(tmp_path / "repo")])
    assert result.exit_code == 0
    assert captured == [1]


def test_download_cli_rejects_invalid_quality_before_provider(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["download", "Reuters", "--quality", "low", "--repository", str(tmp_path / "repo")],
    )
    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert not (tmp_path / "repo").exists()


@pytest.mark.parametrize("timeout", ["4", "61"])
def test_download_cli_rejects_timeout_outside_five_to_sixty(timeout: str) -> None:
    result = runner.invoke(app, ["download", "Reuters", "--discovery-timeout", timeout])
    assert result.exit_code == cli.EXIT_INVALID_INPUT


def test_download_timeout_is_sanitized_and_creates_no_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    marker = "SYNTHETIC-COOKIE-URL-PATH-MARKER"

    class TimeoutIncremental:
        def candidates(
            self,
            target: DiscoveryTarget,
            remaining: int,
            existing_identities: frozenset[str],
            timeout_seconds: int,
            max_scan: int = 100,
        ) -> Iterator[DiscoveryBatch]:
            del target, remaining, existing_identities, timeout_seconds, max_scan
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
            yield

    class UnexpectedMedia:
        def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
            raise AssertionError("media provider must not run after discovery timeout")

    monkeypatch.setattr(cli, "_download_incremental_provider", lambda *args: TimeoutIncremental())
    monkeypatch.setattr(cli, "_media_provider_factory", UnexpectedMedia)
    repository = tmp_path / marker
    result = runner.invoke(
        app,
        [
            "download",
            "Reuters",
            "--limit",
            "2",
            "--discovery-timeout",
            "5",
            "--repository",
            str(repository),
        ],
    )

    assert result.exit_code == cli.EXIT_TRANSIENT
    assert "PROVIDER_TIMEOUT" in result.stderr
    assert marker not in result.stdout + result.stderr
    assert "Traceback" not in result.stderr
    assert not (repository / "catalog.sqlite3").exists()
    assert not list(repository.rglob("video.*"))
    assert not list(repository.rglob("metadata.json"))
    assert not list(repository.rglob("*.part"))
    assert not list(repository.rglob("*.tmp"))
    manifest = json.loads((repository / "manifests/latest.json").read_text())
    assert manifest["complete"] is False
    assert manifest["total_after"] == 0


def test_download_cli_rejects_mutually_exclusive_auth_without_disclosure(
    tmp_path: Path,
) -> None:
    marker = "SYNTHETIC-LOCAL-COOKIE-MARKER"
    cookie_file = tmp_path / marker
    cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "download",
            "Reuters",
            "--auth-browser",
            "firefox",
            "--auth-profile",
            "synthetic-profile",
            "--cookies-file",
            str(cookie_file),
        ],
    )

    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert marker not in result.stdout + result.stderr


@pytest.mark.parametrize("kind", ["missing", "directory", "symlink"])
def test_download_cli_rejects_invalid_cookie_file_without_path(tmp_path: Path, kind: str) -> None:
    marker = "SYNTHETIC-LOCAL-COOKIE-MARKER"
    cookie_file = tmp_path / marker
    if kind == "directory":
        cookie_file.mkdir()
    elif kind == "symlink":
        target = tmp_path / "target"
        target.write_text("unused", encoding="utf-8")
        cookie_file.symlink_to(target)

    result = runner.invoke(
        app,
        ["download", "Reuters", "--cookies-file", str(cookie_file)],
    )

    assert result.exit_code == cli.EXIT_INVALID_INPUT
    assert "cookie file configuration is invalid" in result.stderr
    assert marker not in result.stdout + result.stderr
