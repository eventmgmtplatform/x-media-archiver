"""CLI tests for the bounded B04 download command."""

import hashlib
import json
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


def test_download_json_is_stable_and_omits_ephemeral_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", Discovery)
    monkeypatch.setattr(cli, "_media_provider_factory", Media)
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


@pytest.mark.parametrize("limit", ["0", "6"])
def test_download_cli_rejects_limit_outside_one_to_five(limit: str) -> None:
    result = runner.invoke(app, ["download", "Reuters", "--limit", limit])
    assert result.exit_code == cli.EXIT_INVALID_INPUT


@pytest.mark.parametrize("timeout", ["4", "181"])
def test_download_cli_rejects_timeout_outside_five_to_one_eighty(timeout: str) -> None:
    result = runner.invoke(app, ["download", "Reuters", "--discovery-timeout", timeout])
    assert result.exit_code == cli.EXIT_INVALID_INPUT


def test_download_timeout_is_sanitized_and_creates_no_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    marker = "SYNTHETIC-COOKIE-URL-PATH-MARKER"

    class TimeoutDiscovery:
        def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")

    class UnexpectedMedia:
        def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
            raise AssertionError("media provider must not run after discovery timeout")

    monkeypatch.setattr(cli, "_provider_factory", TimeoutDiscovery)
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
    assert not repository.exists()


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
