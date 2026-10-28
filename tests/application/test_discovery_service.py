from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.application.discovery import DiscoveryService
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import IdentityConflictError

NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


def batch(*, text: str = "report", observed_at: datetime = NOW) -> DiscoveryBatch:
    target = DiscoveryTarget("Reuters")
    asset = DiscoveredAsset("9001", 0, MediaType.VIDEO, 5000, 1280, 720, ("url",))
    post = DiscoveredPost("9001", "123", text, NOW, PostType.POST, (asset,))
    return DiscoveryBatch(
        target,
        "gallery-dl:test",
        DiscoveredProfile("123", "Reuters", "Reuters"),
        (post,),
        observed_at,
        2,
    )


class FakeProvider:
    def __init__(self, result: DiscoveryBatch) -> None:
        self.result = result
        self.calls: list[tuple[DiscoveryTarget, int]] = []

    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        self.calls.append((target, limit))
        return replace(self.result, requested_limit=limit)


def values(items: list[datetime]) -> Iterator[datetime]:
    yield from items


def test_inspect_and_dry_run_have_no_catalog_side_effect(tmp_path: Path) -> None:
    provider = FakeProvider(batch())
    database = tmp_path / "catalog.sqlite3"
    service = DiscoveryService(provider, lambda: SQLiteUnitOfWork(database))

    inspected = service.inspect("@Reuters", 2)
    dry_run = service.sync("Reuters", 2, dry_run=True)

    assert inspected == provider.result
    assert dry_run.dry_run is True
    assert dry_run.run_id is None
    assert not database.exists()
    assert [call[0].handle for call in provider.calls] == ["Reuters", "Reuters"]


def test_sync_persists_catalog_and_is_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    times = values([NOW, NOW + timedelta(seconds=1)] * 2)
    run_ids = iter(["run-1", "run-2"])
    provider = FakeProvider(batch())
    service = DiscoveryService(
        provider,
        lambda: SQLiteUnitOfWork(database),
        lambda: next(times),
        lambda: next(run_ids),
    )

    first = service.sync("Reuters", 2)
    second = service.sync("Reuters", 2)

    assert first.run_id == "run-1"
    assert second.run_id == "run-2"
    with SQLiteUnitOfWork(database) as unit:
        assert unit.catalog.get_profile("123") is not None
        assert unit.catalog.get_post("9001") is not None
        assert unit.catalog.get_media_asset("9001:0") is not None
        assert unit.catalog.get_discovery_run("run-1") is not None
        assert unit.catalog.get_discovery_run("run-2") is not None


def test_profile_observation_update_preserves_created_at(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    first = DiscoveryService(
        FakeProvider(batch()),
        lambda: SQLiteUnitOfWork(database),
        lambda: NOW,
        lambda: "run-1",
    )
    later = NOW + timedelta(days=1)
    second = DiscoveryService(
        FakeProvider(batch(observed_at=later)),
        lambda: SQLiteUnitOfWork(database),
        lambda: later,
        lambda: "run-2",
    )
    first.sync("Reuters", 1)
    second.sync("Reuters", 1)

    with SQLiteUnitOfWork(database) as unit:
        profile = unit.catalog.get_profile("123")
        assert profile is not None
        assert profile.created_at == NOW
        assert profile.observed_at == later


def test_sync_requires_unit_of_work_and_rolls_back_conflict(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="unit of work"):
        DiscoveryService(FakeProvider(batch())).sync("Reuters", 1)

    database = tmp_path / "catalog.sqlite3"
    DiscoveryService(
        FakeProvider(batch()),
        lambda: SQLiteUnitOfWork(database),
        lambda: NOW,
        lambda: "run-1",
    ).sync("Reuters", 1)
    with pytest.raises(IdentityConflictError):
        DiscoveryService(
            FakeProvider(batch(text="changed")),
            lambda: SQLiteUnitOfWork(database),
            lambda: NOW,
            lambda: "run-conflict",
        ).sync("Reuters", 1)
    with SQLiteUnitOfWork(database) as unit:
        assert unit.catalog.get_discovery_run("run-conflict") is None


def test_application_rejects_inconsistent_provider_limit() -> None:
    from xma.domain.errors import DiscoveryContractError

    class InconsistentProvider(FakeProvider):
        def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
            return self.result

    service = DiscoveryService(InconsistentProvider(batch()))
    with pytest.raises(DiscoveryContractError):
        service.inspect("Reuters", 1)
    with pytest.raises(DiscoveryContractError):
        service.inspect("Reuters", 0)
    assert service.inspect("Reuters", 2).cursor is None


def test_rotated_variants_do_not_conflict_or_persist_secrets(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite3"
    provider = FakeProvider(batch())
    service = DiscoveryService(provider, lambda: SQLiteUnitOfWork(database))
    for signature in ("first-secret", "rotated-secret"):
        original = batch()
        post = original.posts[0]
        asset = replace(post.assets[0], variants=(f"https://video.test/a?sig={signature}",))
        provider.result = replace(original, posts=(replace(post, assets=(asset,)),))
        service.sync("Reuters", 2)
    with SQLiteUnitOfWork(database) as unit:
        persisted = unit.catalog.get_media_asset("9001:0")
        assert persisted is not None
        assert persisted.variants == ("metadata-only",)
    import sqlite3

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT count(*) FROM media_assets").fetchone()[0] == 1
    assert b"secret" not in database.read_bytes()
