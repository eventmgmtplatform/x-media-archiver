"""CLI foundation and B03 command tests."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xma.cli as cli
from xma import __version__
from xma.cli import app
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import DiscoveryRestrictedError

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
