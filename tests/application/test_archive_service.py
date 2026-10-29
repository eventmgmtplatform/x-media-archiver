"""Offline B05 checkpoints, paging, cooldown and locking."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import pytest

from xma.adapters.archive import RepositoryArchiveLock, SQLiteArchiveStore
from xma.application.archive import ArchiveService
from xma.domain.archive import ArchiveRequest, ArchiveStatus
from xma.domain.download import DownloadSummary
from xma.domain.errors import CatalogError, DomainError

NOW = datetime(2026, 10, 29, tzinfo=UTC)


class Download:
    def __init__(self, existing: int = 0) -> None:
        self.total = existing
        self.calls: list[int] = []

    def execute_incremental(self, request: Any, *args: object) -> DownloadSummary:
        self.calls.append(request.limit)
        before = self.total
        self.total = max(self.total, request.limit)
        return DownloadSummary(
            request.target,
            request.limit,
            self.total - before,
            before,
            0,
            f"page-{len(self.calls)}",
            (),
            before,
            self.total,
            True,
        )


def service(tmp_path: Path, download: Download, sleeps: list[float]) -> ArchiveService:
    repository = tmp_path / "repository"
    return ArchiveService(
        cast(Any, download),
        cast(Any, object()),
        SQLiteArchiveStore(repository / "catalog.sqlite3"),
        RepositoryArchiveLock(repository),
        clock=lambda: NOW,
        monotonic=lambda: 1.0,
        sleeper=sleeps.append,
        run_id_factory=lambda: "archive-run",
    )


def test_archive_pages_zero_to_ten_and_persists_checkpoint(tmp_path: Path) -> None:
    download, sleeps = Download(), []  # type: Download, list[float]
    result = service(tmp_path, download, sleeps).execute(
        ArchiveRequest.create("BBCWorld", 10, 2, 2), 30, lambda message: None
    )
    assert result.status is ArchiveStatus.COMPLETED
    assert result.downloaded_total == 10
    assert result.page_number == 5
    assert download.calls == [2, 4, 6, 8, 10]
    assert sleeps == [2.0, 2.0, 2.0, 2.0]
    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored is not None and restored.public_dict()["remaining"] == 0


def test_archive_five_to_ten_only_requests_new_total(tmp_path: Path) -> None:
    download, sleeps = Download(5), []  # type: Download, list[float]
    result = service(tmp_path, download, sleeps).execute(
        ArchiveRequest.create("BBCWorld", 10, 2, 1), 30, lambda message: None
    )
    assert result.existing_before == 5
    assert result.downloaded_total == 10
    assert download.calls == [2, 7, 9, 10]


def test_completed_run_finishes_offline_and_incompatible_target_fails(tmp_path: Path) -> None:
    download = Download()
    archive = service(tmp_path, download, [])
    request = ArchiveRequest.create("BBCWorld", 1, 1, 1)
    archive.execute(request, 30, lambda message: None)
    assert archive.execute(request, 30, lambda message: None).status is ArchiveStatus.COMPLETED
    assert download.calls == [1]
    with pytest.raises(DomainError, match="target conflicts"):
        archive.execute(ArchiveRequest.create("Reuters", 2, 1, 1), 30, lambda message: None)


def test_resumed_run_respects_persisted_cooldown(tmp_path: Path) -> None:
    download, sleeps = Download(), []  # type: Download, list[float]
    store = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3")
    archive = service(tmp_path, download, sleeps)
    result = archive.execute(ArchiveRequest.create("BBCWorld", 2, 1, 3), 30, lambda message: None)
    paused = result.__class__(
        result.run_id,
        result.target,
        3,
        1,
        3,
        ArchiveStatus.PAUSED,
        result.existing_before,
        2,
        result.page_number,
        result.checkpoint_strategy,
        result.created_at,
        NOW,
        None,
        "PROVIDER_TIMEOUT",
        NOW + timedelta(seconds=3),
    )
    store.put(paused)
    archive.execute(ArchiveRequest.create("BBCWorld", 3, 1, 3), 30, lambda message: None)
    assert 3.0 in sleeps


def test_repository_lock_rejects_second_holder_and_releases(tmp_path: Path) -> None:
    first = RepositoryArchiveLock(tmp_path)
    with (
        first,
        pytest.raises(CatalogError, match="already in use"),
        RepositoryArchiveLock(tmp_path),
    ):
        pass
    with RepositoryArchiveLock(tmp_path):
        pass
