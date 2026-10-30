"""Offline B05 checkpoints, paging, cooldown and locking."""

import sqlite3
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from xma.adapters.archive import RepositoryArchiveLock, SQLiteArchiveStore
from xma.application.archive import ArchiveService
from xma.domain.archive import (
    ArchiveMode,
    ArchiveRequest,
    ArchiveRun,
    ArchiveStatus,
    CompletionReason,
)
from xma.domain.download import DownloadSummary
from xma.domain.errors import (
    ArchiveUnexpectedError,
    CatalogError,
    DiscoveryTransientError,
    DomainError,
    DownloadConflictError,
    DownloadError,
)

NOW = datetime(2026, 10, 29, tzinfo=UTC)


class Download:
    def __init__(self, existing: int = 0) -> None:
        self.total = existing
        self.calls: list[int] = []
        self.verified_handles: list[str] = []

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

    def verified_total(self, handle: str) -> int:
        self.verified_handles.append(handle)
        return self.total


class CountingStore(SQLiteArchiveStore):
    def __init__(self, database: Path) -> None:
        super().__init__(database)
        self.put_calls = 0

    def put(self, run: ArchiveRun) -> None:
        self.put_calls += 1
        super().put(run)


class InconsistentRepositoryDownload(Download):
    def verified_total(self, handle: str) -> int:
        self.verified_handles.append(handle)
        raise DownloadError("repository integrity verification failed")


def terminal_all_run(
    *,
    target: str = "BBCWorld",
    total: int = 23,
    reason: CompletionReason = CompletionReason.PROVIDER_EXHAUSTED,
    failed_total: int = 0,
) -> ArchiveRun:
    return ArchiveRun(
        "terminal-all-run",
        target,
        1,
        5,
        2,
        ArchiveStatus.COMPLETED,
        0,
        total,
        5,
        "RESCAN_DEDUP_V2",
        NOW,
        NOW,
        NOW,
        next_allowed_at=NOW + timedelta(seconds=2),
        mode=ArchiveMode.ALL,
        completion_reason=reason,
        failed_total=failed_total,
        max_runtime_seconds=600,
        resumed_at=NOW - timedelta(hours=1),
    )


def terminal_all_service(
    tmp_path: Path, completed: ArchiveRun, download: Download
) -> tuple[ArchiveService, CountingStore]:
    store = CountingStore(tmp_path / "repository/catalog.sqlite3")
    store.put(completed)
    store.put_calls = 0
    return (
        ArchiveService(
            cast(Any, download),
            cast(Any, object()),
            store,
            RepositoryArchiveLock(tmp_path / "repository"),
            clock=lambda: NOW + timedelta(hours=1),
        ),
        store,
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
    assert download.calls == [7, 9, 10]


def test_all_twenty_to_fifty_pauses_at_safety_cap(tmp_path: Path) -> None:
    download, sleeps = Download(20), []  # type: Download, list[float]
    result = service(tmp_path, download, sleeps).execute(
        ArchiveRequest.create_all(
            "BBCWorld",
            5,
            1,
            max_items=50,
            max_runtime_seconds=600,
            min_free_space_gib=5,
        ),
        30,
        lambda message: None,
    )
    assert result.mode is ArchiveMode.ALL
    assert result.status is ArchiveStatus.PAUSED
    assert result.completion_reason is CompletionReason.SAFETY_CAP_REACHED
    assert result.downloaded_total == 50
    assert result.page_number == 6
    assert download.calls == [25, 30, 35, 40, 45, 50]
    assert result.public_dict()["resumable"] is True


class ExhaustedDownload(Download):
    def execute_incremental(self, request: Any, *args: object) -> DownloadSummary:
        del args
        return DownloadSummary(
            request.target,
            request.limit,
            0,
            self.total,
            0,
            "exhausted",
            (),
            self.total,
            self.total,
            False,
            True,
        )


def test_all_completes_only_on_explicit_provider_exhaustion(tmp_path: Path) -> None:
    result = service(tmp_path, ExhaustedDownload(), []).execute(
        ArchiveRequest.create_all("BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5),
        30,
        lambda message: None,
    )
    assert result.status is ArchiveStatus.COMPLETED
    assert result.completion_reason is CompletionReason.PROVIDER_EXHAUSTED
    assert result.downloaded_total == 0


def test_completed_all_provider_exhaustion_is_offline_idempotent_noop(tmp_path: Path) -> None:
    completed = terminal_all_run()
    download = Download(23)
    archive, store = terminal_all_service(tmp_path, completed, download)

    result = archive.execute(
        ArchiveRequest.create_all("BBCWorld", 5, 2, max_runtime_seconds=600, min_free_space_gib=5),
        30,
        lambda message: None,
    )

    assert result == completed
    assert store.put_calls == 0
    assert download.calls == []
    assert download.verified_handles == ["BBCWorld"]
    assert store.latest() == completed


@pytest.mark.parametrize("resume", [False, True])
def test_completed_all_noop_preserves_every_durable_field_and_manifest(
    tmp_path: Path, resume: bool
) -> None:
    completed = terminal_all_run()
    download = Download(completed.downloaded_total)
    archive, store = terminal_all_service(tmp_path, completed, download)
    manifest = tmp_path / "repository/manifest.json"
    manifest.write_text('{"certified":true}\n', encoding="utf-8")
    before_hash = sha256(manifest.read_bytes()).hexdigest()
    request = ArchiveRequest.create_all(
        "BBCWorld",
        3,
        1,
        max_items=50,
        max_runtime_seconds=1200,
        min_free_space_gib=6,
        resume=resume,
    )

    first = archive.execute(request, 30, lambda message: None)
    second = archive.execute(request, 30, lambda message: None)

    assert first == completed
    assert second == completed
    assert first.run_id == completed.run_id
    assert first.updated_at == completed.updated_at
    assert first.resumed_at == completed.resumed_at
    assert first.max_items == completed.max_items
    assert store.put_calls == 0
    assert download.calls == []
    assert download.verified_handles == ["BBCWorld", "BBCWorld"]
    assert sha256(manifest.read_bytes()).hexdigest() == before_hash
    assert store.latest() == completed


@pytest.mark.parametrize("repository_total", [22, 24])
def test_completed_all_noop_rejects_checkpoint_repository_mismatch(
    tmp_path: Path, repository_total: int
) -> None:
    completed = terminal_all_run(total=23)
    download = Download(repository_total)
    archive, store = terminal_all_service(tmp_path, completed, download)

    with pytest.raises(DomainError, match="checkpoint is inconsistent"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )

    assert store.put_calls == 0
    assert download.calls == []


def test_completed_all_noop_rejects_inconsistent_repository(tmp_path: Path) -> None:
    completed = terminal_all_run()
    download = InconsistentRepositoryDownload(23)
    archive, store = terminal_all_service(tmp_path, completed, download)

    with pytest.raises(DownloadError, match="integrity verification failed"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )

    assert store.put_calls == 1
    assert download.calls == []


def test_completed_all_noop_rejects_target_and_lower_cap_without_external_calls(
    tmp_path: Path,
) -> None:
    completed = terminal_all_run()
    download = Download(23)
    archive, store = terminal_all_service(tmp_path, completed, download)
    with pytest.raises(DomainError, match="target conflicts"):
        archive.execute(
            ArchiveRequest.create_all(
                "Reuters", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )
    with pytest.raises(DomainError, match="max-items is below"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld",
                5,
                1,
                max_items=22,
                max_runtime_seconds=600,
                min_free_space_gib=5,
            ),
            30,
            lambda message: None,
        )
    assert store.put_calls == 0
    assert download.calls == []
    assert download.verified_handles == ["BBCWorld"]


@pytest.mark.parametrize(
    ("reason", "failed_total"),
    [
        (CompletionReason.REQUESTED_TOTAL_REACHED, 0),
        (CompletionReason.PROVIDER_EXHAUSTED, 1),
    ],
)
def test_completed_all_noop_rejects_uncertified_terminal(
    tmp_path: Path, reason: CompletionReason, failed_total: int
) -> None:
    completed = terminal_all_run(reason=reason, failed_total=failed_total)
    download = Download(23)
    archive, store = terminal_all_service(tmp_path, completed, download)

    with pytest.raises(DomainError, match="checkpoint is inconsistent"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )

    assert store.put_calls == 0
    assert download.calls == []


class PartialExhaustedDownload(Download):
    def __init__(self, existing: int, added: int, failed: int = 0) -> None:
        super().__init__(existing)
        self.added = added
        self.failed = failed

    def execute_incremental(self, request: Any, *args: object) -> DownloadSummary:
        del args
        before = self.total
        self.total += self.added
        return DownloadSummary(
            request.target,
            request.limit,
            self.added,
            before,
            self.failed,
            "partial-exhausted",
            tuple({"identity": str(index)} for index in range(self.total)),
            before,
            self.total,
            False,
            True,
        )


@pytest.mark.parametrize(
    ("added", "failed", "expected_total", "expected_page"),
    [(0, 0, 20, 0), (1, 0, 21, 1), (3, 0, 23, 1), (2, 1, 22, 1)],
)
def test_all_reconciles_partial_final_page_before_completing(
    tmp_path: Path,
    added: int,
    failed: int,
    expected_total: int,
    expected_page: int,
) -> None:
    download = PartialExhaustedDownload(20, added, failed)
    result = service(tmp_path, download, []).execute(
        ArchiveRequest.create_all("BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5),
        30,
        lambda message: None,
    )

    assert result.status is ArchiveStatus.COMPLETED
    assert result.completion_reason is CompletionReason.PROVIDER_EXHAUSTED
    assert result.downloaded_total == expected_total
    assert result.failed_total == failed
    assert result.page_number == expected_page
    assert result.public_dict()["complete"] is True
    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored == result
    with sqlite3.connect(tmp_path / "repository/catalog.sqlite3") as connection:
        assert connection.execute(
            "SELECT known_identity_count,last_completed_page FROM archive_checkpoints"
        ).fetchone() == (expected_total, expected_page)


class FailingCompletionStore(SQLiteArchiveStore):
    def __init__(self, database: Path) -> None:
        super().__init__(database)
        self.failed_once = False

    def put(self, run: ArchiveRun) -> None:
        if run.status is ArchiveStatus.COMPLETED and not self.failed_once:
            self.failed_once = True
            raise sqlite3.IntegrityError("synthetic checkpoint failure")
        super().put(run)


def test_partial_exhaustion_checkpoint_failure_preserves_previous_checkpoint(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    store = FailingCompletionStore(repository / "catalog.sqlite3")
    archive = ArchiveService(
        cast(Any, PartialExhaustedDownload(20, 3)),
        cast(Any, object()),
        store,
        RepositoryArchiveLock(repository),
        clock=lambda: NOW,
        monotonic=lambda: 1.0,
        sleeper=lambda seconds: None,
        run_id_factory=lambda: "archive-run",
    )

    with pytest.raises(ArchiveUnexpectedError):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )

    restored = store.latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.FAILED
    assert restored.downloaded_total == 20
    assert restored.page_number == 0
    assert restored.last_error_code == "UNEXPECTED_FAILURE"
    with sqlite3.connect(repository / "catalog.sqlite3") as connection:
        assert connection.execute(
            "SELECT known_identity_count,last_completed_page FROM archive_checkpoints"
        ).fetchone() == (20, 0)


class MismatchedPartialExhaustedDownload(PartialExhaustedDownload):
    def execute_incremental(self, request: Any, *args: object) -> DownloadSummary:
        summary = super().execute_incremental(request, *args)
        return replace(summary, total_after=summary.total_after + 1)


def test_partial_exhaustion_repository_mismatch_fails_closed(tmp_path: Path) -> None:
    archive = service(tmp_path, MismatchedPartialExhaustedDownload(20, 3), [])

    with pytest.raises(DownloadConflictError, match="catalog and filesystem"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )

    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.FAILED
    assert restored.downloaded_total == 20
    assert restored.page_number == 0
    assert restored.last_error_code == "REPOSITORY_INCONSISTENT"


def test_transient_text_cannot_impersonate_provider_exhaustion(tmp_path: Path) -> None:
    archive = service(
        tmp_path,
        FailingDownload(DiscoveryTransientError("contains [PROVIDER_EXHAUSTED] text")),
        [],
    )
    with pytest.raises(DiscoveryTransientError):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5
            ),
            30,
            lambda message: None,
        )
    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.PAUSED
    assert restored.completion_reason is CompletionReason.PROVIDER_TRANSIENT


@pytest.mark.parametrize(
    ("cap", "expected_calls", "expected_status"),
    [
        (10, [], None),
        (20, [], ArchiveStatus.PAUSED),
        (21, [21], ArchiveStatus.PAUSED),
        (50, [25, 30, 35, 40, 45, 50], ArchiveStatus.PAUSED),
    ],
)
def test_all_cap_is_checked_against_twenty_verified(
    tmp_path: Path,
    cap: int,
    expected_calls: list[int],
    expected_status: ArchiveStatus | None,
) -> None:
    download = Download(20)
    archive = service(tmp_path, download, [])
    request = ArchiveRequest.create_all(
        "BBCWorld", 5, 1, max_items=cap, max_runtime_seconds=600, min_free_space_gib=5
    )
    if expected_status is None:
        with pytest.raises(DomainError, match="below verified"):
            archive.execute(request, 30, lambda message: None)
        assert SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest() is None
    else:
        result = archive.execute(request, 30, lambda message: None)
        assert result.status is expected_status
        assert result.completion_reason is CompletionReason.SAFETY_CAP_REACHED
        assert result.downloaded_total == cap
    assert download.calls == expected_calls


def test_all_resume_requires_compatible_paused_run(tmp_path: Path) -> None:
    download = Download()
    archive = service(tmp_path, download, [])
    with pytest.raises(DomainError, match="compatible paused ALL"):
        archive.execute(
            ArchiveRequest.create_all(
                "BBCWorld",
                5,
                1,
                max_items=10,
                max_runtime_seconds=600,
                min_free_space_gib=5,
                resume=True,
            ),
            30,
            lambda message: None,
        )

    paused = archive.execute(
        ArchiveRequest.create_all(
            "BBCWorld", 5, 1, max_items=5, max_runtime_seconds=600, min_free_space_gib=5
        ),
        30,
        lambda message: None,
    )
    assert paused.status is ArchiveStatus.PAUSED
    resumed = archive.execute(
        ArchiveRequest.create_all(
            "BBCWorld",
            5,
            1,
            max_items=10,
            max_runtime_seconds=600,
            min_free_space_gib=5,
            resume=True,
        ),
        30,
        lambda message: None,
    )
    assert resumed.downloaded_total == 10
    assert resumed.status is ArchiveStatus.PAUSED


def test_all_resumes_failed_domain_boundary_from_twenty_to_fifty(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    store = SQLiteArchiveStore(repository / "catalog.sqlite3")
    store.put(
        ArchiveRun(
            "failed-prm0050",
            "BBCWorld",
            50,
            5,
            2,
            ArchiveStatus.FAILED,
            0,
            20,
            4,
            "RESCAN_DEDUP_V2",
            NOW,
            NOW,
            last_error_code="DomainError",
            mode=ArchiveMode.ALL,
            completion_reason=CompletionReason.FAILED,
            max_items=50,
            max_runtime_seconds=1800,
            min_free_space_bytes=5 * 1024**3,
        )
    )
    download = Download(20)
    archive = service(tmp_path, download, [])

    result = archive.execute(
        ArchiveRequest.create_all(
            "BBCWorld",
            5,
            2,
            max_items=50,
            max_runtime_seconds=1800,
            min_free_space_gib=5,
            resume=True,
        ),
        30,
        lambda message: None,
    )

    assert download.calls == [25, 30, 35, 40, 45, 50]
    assert result.status is ArchiveStatus.PAUSED
    assert result.completion_reason is CompletionReason.SAFETY_CAP_REACHED
    assert result.downloaded_total == 50
    assert result.page_number == 10
    restored = store.latest()
    assert restored == result


def test_all_pauses_before_discovery_on_low_space(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "xma.application.archive.shutil.disk_usage",
        lambda path: SimpleNamespace(free=1),
    )
    download = Download()
    result = service(tmp_path, download, []).execute(
        ArchiveRequest.create_all("BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5),
        30,
        lambda message: None,
    )
    assert result.status is ArchiveStatus.PAUSED
    assert result.completion_reason is CompletionReason.LOW_DISK_SPACE
    assert download.calls == []


def test_all_pauses_at_runtime_without_leaving_running(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    ticks = iter([0.0, 601.0])
    archive = ArchiveService(
        cast(Any, Download()),
        cast(Any, object()),
        SQLiteArchiveStore(repository / "catalog.sqlite3"),
        RepositoryArchiveLock(repository),
        clock=lambda: NOW,
        monotonic=lambda: next(ticks),
        sleeper=lambda seconds: None,
        run_id_factory=lambda: "runtime-run",
    )
    result = archive.execute(
        ArchiveRequest.create_all("BBCWorld", 5, 1, max_runtime_seconds=600, min_free_space_gib=5),
        30,
        lambda message: None,
    )
    assert result.status is ArchiveStatus.PAUSED
    assert result.completion_reason is CompletionReason.MAX_RUNTIME_REACHED


def test_reconciles_defective_running_run_five_to_seven_nine_ten(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    store = SQLiteArchiveStore(repository / "catalog.sqlite3")
    store.put(
        ArchiveRun(
            "defective-run",
            "BBCWorld",
            10,
            2,
            1,
            ArchiveStatus.RUNNING,
            0,
            0,
            0,
            "RESCAN_DEDUP_V1",
            NOW,
            NOW,
        )
    )
    download, sleeps = Download(5), []  # type: Download, list[float]
    result = service(tmp_path, download, sleeps).execute(
        ArchiveRequest.create("BBCWorld", 10, 2, 1), 30, lambda message: None
    )
    assert download.calls == [7, 9, 10]
    assert result.existing_before == 5
    assert result.downloaded_total == 10
    assert result.page_number == 3
    assert result.status is ArchiveStatus.COMPLETED
    assert result.remaining == 0


class FailingDownload(Download):
    def __init__(self, error: BaseException) -> None:
        super().__init__()
        self.error = error

    def execute_incremental(self, request: Any, *args: object) -> DownloadSummary:
        del request, args
        raise self.error


@pytest.mark.parametrize(
    ("error", "status", "code"),
    [
        (DomainError("invalid"), ArchiveStatus.FAILED, "DomainError"),
        (DownloadError("failed"), ArchiveStatus.FAILED, "DownloadError"),
        (
            DiscoveryTransientError("timeout"),
            ArchiveStatus.PAUSED,
            "DiscoveryTransientError",
        ),
        (InterruptedError(), ArchiveStatus.PAUSED, "INTERRUPTED"),
        (KeyboardInterrupt(), ArchiveStatus.PAUSED, "INTERRUPTED"),
    ],
)
def test_every_exit_persists_terminal_state(
    tmp_path: Path, error: BaseException, status: ArchiveStatus, code: str
) -> None:
    archive = service(tmp_path, FailingDownload(error), [])
    with pytest.raises(type(error)):
        archive.execute(ArchiveRequest.create("BBCWorld", 1, 1, 1), 30, lambda message: None)
    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored is not None
    assert restored.status is status
    assert restored.last_error_code == code


def test_unexpected_error_is_wrapped_and_preserved_as_internal_cause(tmp_path: Path) -> None:
    original = RuntimeError("secret path=/private token=synthetic")
    archive = service(tmp_path, FailingDownload(original), [])
    with pytest.raises(ArchiveUnexpectedError, match="archive failed unexpectedly") as captured:
        archive.execute(ArchiveRequest.create("BBCWorld", 1, 1, 1), 30, lambda message: None)
    assert captured.value.__cause__ is original
    assert "secret" not in str(captured.value)
    restored = SQLiteArchiveStore(tmp_path / "repository/catalog.sqlite3").latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.FAILED
    assert restored.last_error_code == "UNEXPECTED_FAILURE"


def test_checkpoint_ahead_of_repository_fails_without_discovery(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    store = SQLiteArchiveStore(repository / "catalog.sqlite3")
    store.put(
        ArchiveRun(
            "ahead",
            "BBCWorld",
            10,
            2,
            1,
            ArchiveStatus.PAUSED,
            5,
            6,
            1,
            "RESCAN_DEDUP_V1",
            NOW,
            NOW,
        )
    )
    download = Download(5)
    with pytest.raises(DomainError, match="checkpoint is inconsistent"):
        service(tmp_path, download, []).execute(
            ArchiveRequest.create("BBCWorld", 10, 2, 1), 30, lambda message: None
        )
    restored = store.latest()
    assert restored is not None
    assert restored.status is ArchiveStatus.FAILED
    assert restored.last_error_code == "CHECKPOINT_AHEAD_OF_REPOSITORY"
    assert download.calls == []


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


def test_archive_store_updates_existing_before_and_rolls_back_atomically(tmp_path: Path) -> None:
    database = tmp_path / "repository/catalog.sqlite3"
    store = SQLiteArchiveStore(database)
    original = ArchiveRun(
        "durable-run",
        "BBCWorld",
        10,
        2,
        2,
        ArchiveStatus.COMPLETED,
        0,
        10,
        3,
        "RESCAN_DEDUP_V1",
        NOW,
        NOW,
        NOW,
    )
    store.put(original)
    repaired = replace(original, existing_before=5, updated_at=NOW + timedelta(seconds=1))

    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TRIGGER fail_checkpoint BEFORE UPDATE ON archive_checkpoints "
            "BEGIN SELECT RAISE(ABORT, 'synthetic'); END"
        )
    with pytest.raises(sqlite3.IntegrityError):
        store.put(repaired)
    rolled_back = store.latest()
    assert rolled_back == original

    with sqlite3.connect(database) as connection:
        connection.execute("DROP TRIGGER fail_checkpoint")
    store.put(repaired)
    restored = store.latest()
    assert restored is not None
    assert restored.run_id == original.run_id
    assert restored.created_at == original.created_at
    assert restored.existing_before == 5
    assert restored.downloaded_total == 10
    assert restored.page_number == 3
    assert restored.status is ArchiveStatus.COMPLETED
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT known_identity_count,last_completed_page FROM archive_checkpoints"
        ).fetchone() == (10, 3)
