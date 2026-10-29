import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import xma.adapters.catalog.migrations as migrations
from xma.adapters.catalog.migrations import LATEST_SCHEMA_VERSION, migrate
from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.domain.enums import DownloadStatus, MediaType, PostType, RunStatus
from xma.domain.errors import IdentityConflictError
from xma.domain.models import Artifact, DiscoveryRun, DownloadJob, MediaAsset, Post, Profile

NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


def aggregates() -> tuple[Profile, Post, MediaAsset, DiscoveryRun, DownloadJob, Artifact]:
    profile = Profile("123", "example", "Example", NOW, NOW, NOW)
    post = Post("456", "123", "https://x.com/i/status/456", "text", NOW, PostType.POST)
    asset = MediaAsset("456", 0, MediaType.VIDEO, 5000, 1920, 1080, ("hd", "sd"))
    run = DiscoveryRun("run-1", "fixtures", NOW, RunStatus.COMPLETED, NOW, None, 1, 0)
    job = DownloadJob("job-1", asset.asset_id, run.run_id, DownloadStatus.DISCOVERED, 0, NOW, NOW)
    artifact = Artifact(
        "artifact-1", job.job_id, "profiles/example/media.mp4", "video/mp4", 100, "a" * 64, NOW
    )
    return profile, post, asset, run, job, artifact


def put_all(catalog: object) -> None:
    profile, post, asset, run, job, artifact = aggregates()
    catalog.put_profile(profile)  # type: ignore[attr-defined]
    catalog.put_post(post)  # type: ignore[attr-defined]
    catalog.put_media_asset(asset)  # type: ignore[attr-defined]
    catalog.put_discovery_run(run)  # type: ignore[attr-defined]
    catalog.put_download_job(job)  # type: ignore[attr-defined]
    catalog.put_artifact(artifact)  # type: ignore[attr-defined]


def test_migration_from_empty_database_is_idempotent() -> None:
    connection = sqlite3.connect(":memory:", isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    assert migrate(connection) == LATEST_SCHEMA_VERSION
    assert migrate(connection) == LATEST_SCHEMA_VERSION
    assert connection.execute("SELECT COUNT(*) FROM schema_version").fetchone() == (2,)
    assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)
    connection.close()


def test_failed_migration_rolls_back_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = sqlite3.connect(":memory:", isolation_level=None)
    monkeypatch.setattr(
        migrations, "_migration_sql", lambda version: "CREATE TABLE partial(id); BAD SQL;"
    )
    with pytest.raises(sqlite3.OperationalError):
        migrate(connection)
    assert connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
    ).fetchone() == (0,)
    connection.close()


def test_crud_idempotence_and_persistence_between_reopens(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    expected = aggregates()
    with SQLiteUnitOfWork(database) as unit:
        put_all(unit.catalog)
        put_all(unit.catalog)
    with SQLiteUnitOfWork(database) as unit:
        catalog = unit.catalog
        actual = (
            catalog.get_profile("123"),
            catalog.get_post("456"),
            catalog.get_media_asset("456:0"),
            catalog.get_discovery_run("run-1"),
            catalog.get_download_job("job-1"),
            catalog.get_artifact("artifact-1"),
        )
        assert actual == expected


def test_profile_handle_update_preserves_stable_identity(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    original = aggregates()[0]
    changed = Profile(
        "123", "renamed", "New Name", NOW + timedelta(days=1), NOW, NOW + timedelta(days=1)
    )
    with SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_profile(original)
        unit.catalog.put_profile(changed)
        assert unit.catalog.get_profile("123") == changed


def test_profile_rejects_identity_and_handle_conflicts(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    profile = aggregates()[0]
    other = Profile("999", "other", "Other", NOW, NOW, NOW)
    with SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_profile(profile)
        unit.catalog.put_profile(other)
        with pytest.raises(IdentityConflictError):
            unit.catalog.put_profile(
                Profile("123", "example", "Example", NOW, NOW - timedelta(days=1), NOW)
            )
        with pytest.raises(IdentityConflictError):
            unit.catalog.put_profile(Profile("123", "other", "Example", NOW, NOW, NOW))


def test_identity_conflict_is_explicit(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    profile, post, *_ = aggregates()
    conflicting = Post("456", "123", "https://x.com/i/status/456", "different", NOW, PostType.POST)
    with SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_profile(profile)
        unit.catalog.put_post(post)
        with pytest.raises(IdentityConflictError):
            unit.catalog.put_post(conflicting)


def test_foreign_key_integrity_and_transaction_rollback(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    post = aggregates()[1]
    with pytest.raises(IdentityConflictError), SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_post(post)
    with SQLiteUnitOfWork(database) as unit:
        assert unit.catalog.get_post("456") is None
        assert unit.catalog.get_profile("123") is None


def test_exception_rolls_back_complete_unit_of_work(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    profile = aggregates()[0]
    with pytest.raises(RuntimeError, match="abort"), SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_profile(profile)
        raise RuntimeError("abort")
    with SQLiteUnitOfWork(database) as unit:
        assert unit.catalog.get_profile("123") is None


def test_download_job_update_preserves_identity(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    profile, post, asset, run, job, _ = aggregates()
    with SQLiteUnitOfWork(database) as unit:
        unit.catalog.put_profile(profile)
        unit.catalog.put_post(post)
        unit.catalog.put_media_asset(asset)
        unit.catalog.put_discovery_run(run)
        unit.catalog.put_download_job(job)
        queued = job.transition(DownloadStatus.QUEUED, NOW + timedelta(seconds=1))
        unit.catalog.put_download_job(queued)
        assert unit.catalog.get_download_job("job-1") == queued
        invalid = DownloadJob(
            job.job_id,
            job.asset_id,
            job.run_id,
            DownloadStatus.COMPLETED,
            job.attempts,
            job.created_at,
            NOW + timedelta(seconds=2),
        )
        with pytest.raises(IdentityConflictError, match="valid transition"):
            unit.catalog.put_download_job(invalid)
