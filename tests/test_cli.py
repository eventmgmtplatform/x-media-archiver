"""CLI foundation and B03 command tests."""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xma.cli as cli
from xma import __version__
from xma.adapters.discovery.gallery_dl import GalleryDlDiscoveryProvider, GalleryDlExtraction
from xma.cli import app
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import (
    CatalogError,
    DiscoveryError,
    DiscoveryNotFoundError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
    DiscoveryTransientError,
    IdentityConflictError,
)

runner = CliRunner()
NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


class FakeProvider:
    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        asset = DiscoveredAsset("9001", 0, MediaType.VIDEO, 1000, 1280, 720, ("private",))
        post = DiscoveredPost("9001", "123", "report", NOW, PostType.POST, (asset,))
        return DiscoveryBatch(
            target,
            "fixture:1",
            DiscoveredProfile("123", target.handle, "Reuters"),
            (post,),
            NOW,
            limit,
        )


class RestrictedProvider:
    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        raise DiscoveryRestrictedError("anonymous access unavailable")


def test_help_lists_product_and_version_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Catalog and archive public audiovisual content from X" in result.stdout
    assert "version" in result.stdout


def test_no_arguments_displays_help() -> None:
    result = runner.invoke(app)

    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_version_is_human_readable() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"X Media Archiver {__version__}"


def test_short_version_is_machine_readable() -> None:
    result = runner.invoke(app, ["version", "--short"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_inspect_json_has_no_catalog_or_source_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", FakeProvider)
    result = runner.invoke(app, ["inspect", "@Reuters", "--limit", "2", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["asset_count"] == 1
    assert "private" not in result.stdout
    assert not (tmp_path / "catalog.sqlite3").exists()


def test_sync_writes_catalog_and_dry_run_does_not(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", FakeProvider)
    repository = tmp_path / "repo"
    result = runner.invoke(
        app,
        ["sync", "Reuters", "--limit", "1", "--repository", str(repository), "--json"],
    )
    assert result.exit_code == 0
    assert (repository / "catalog.sqlite3").is_file()
    assert json.loads(result.stdout)["run_id"]

    dry_repository = tmp_path / "dry"
    dry = runner.invoke(
        app,
        [
            "sync",
            "Reuters",
            "--limit",
            "1",
            "--repository",
            str(dry_repository),
            "--dry-run",
        ],
    )
    assert dry.exit_code == 0
    assert "Dry run" in dry.stdout
    assert not dry_repository.exists()


def test_cli_exit_codes_for_invalid_and_restricted_input(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = runner.invoke(app, ["inspect", "https://example.com/nope"])
    assert invalid.exit_code == cli.EXIT_INVALID_INPUT
    assert "invalid input" in invalid.stderr

    monkeypatch.setattr(cli, "_provider_factory", RestrictedProvider)
    restricted = runner.invoke(app, ["inspect", "Reuters"])
    assert restricted.exit_code == cli.EXIT_RESTRICTED
    assert "anonymous access unavailable" in restricted.stderr


def test_human_inspect_renders_observational_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_provider_factory", FakeProvider)
    result = runner.invoke(app, ["inspect", "Reuters", "--limit", "1"])
    assert result.exit_code == 0
    assert "Coverage is observational" in result.stdout
    assert "not complete" in result.stdout


def test_json_preserves_markup_unicode_and_long_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    from dataclasses import replace

    text = "[red]México[/red] " + "á" * 1000

    class TextProvider(FakeProvider):
        def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
            batch = super().discover(target, limit)
            return replace(batch, posts=(replace(batch.posts[0], text=text),))

    monkeypatch.setattr(cli, "_provider_factory", TextProvider)
    for command in (["inspect", "Reuters", "--json"], ["sync", "Reuters", "--dry-run", "--json"]):
        result = runner.invoke(app, command)
        assert result.exit_code == 0
        assert json.loads(result.stdout)["posts"][0]["text"] == text
        assert "México" in result.stdout


def test_sync_normalizes_filesystem_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", FakeProvider)
    blocked = tmp_path / "file"
    blocked.write_text("occupied")
    result = runner.invoke(app, ["sync", "Reuters", "--repository", str(blocked)])
    assert result.exit_code == cli.EXIT_CATALOG_FAILED
    assert "catalog failed" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "error",
    [
        IdentityConflictError("sensitive"),
        sqlite3.OperationalError("sensitive"),
        CatalogError("sensitive"),
    ],
)
def test_sync_normalizes_catalog_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    monkeypatch.setattr(cli, "_provider_factory", FakeProvider)

    def fail(database: Path) -> None:
        raise error

    monkeypatch.setattr(cli, "SQLiteUnitOfWork", fail)
    result = runner.invoke(app, ["sync", "Reuters", "--repository", str(tmp_path)])
    assert result.exit_code == cli.EXIT_CATALOG_FAILED
    assert "sensitive" not in result.stderr


@pytest.mark.parametrize(
    "error,code",
    [
        (DiscoveryNotFoundError("not found"), 7),
        (DiscoveryTransientError("temporary failure"), 8),
        (DiscoveryRateLimitError("rate limited"), 4),
        (DiscoveryError("contract failed"), 5),
    ],
)
def test_external_error_exit_codes(
    monkeypatch: pytest.MonkeyPatch, error: Exception, code: int
) -> None:
    class FailedProvider:
        def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
            raise error

    monkeypatch.setattr(cli, "_provider_factory", FailedProvider)
    result = runner.invoke(app, ["inspect", "Reuters"])
    assert result.exit_code == code
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "invalid_duration",
    [-0.0001, -0.0005, -5e-324, "-0.0001", "-1e-400"],
    ids=["tenth-ms", "half-ms", "negative-subnormal", "string-tenth-ms", "string-extreme"],
)
@pytest.mark.parametrize("command", ["inspect", "sync"])
def test_cli_sanitizes_real_mapper_numeric_contract_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    command: str,
    invalid_duration: object,
) -> None:
    marker = "SYNTHETIC-SIGNED-URL-SECRET"
    record = {
        "type": "video",
        "tweet_id": 9001,
        "author": {"id": 123},
        "num": 1,
        "width": 1280,
        "height": 720,
        "duration": invalid_duration,
        "date": "2026-10-28T12:00:00Z",
        f"_{marker}": marker,
        "_source_url": f"https://media.invalid/video?signature={marker}",
    }
    extraction = GalleryDlExtraction(
        {"user": {"id": 123, "name": "Reuters", "nick": "Reuters"}},
        (record,),
    )
    monkeypatch.setattr(
        cli,
        "_provider_factory",
        lambda: GalleryDlDiscoveryProvider(lambda url, limit: extraction, lambda: NOW),
    )
    repository = tmp_path / "must-not-exist"
    arguments = [command, "Reuters", "--limit", "1"]
    if command == "sync":
        arguments.extend(["--repository", str(repository)])

    result = runner.invoke(app, arguments)

    assert result.exit_code == cli.EXIT_PROVIDER_FAILED
    assert "gallery-dl numeric metadata violates the B03 contract" in result.stderr
    assert "Traceback" not in result.stderr
    assert marker not in result.stdout + result.stderr
    assert not repository.exists()
