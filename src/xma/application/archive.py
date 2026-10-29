"""Durable RESCAN_DEDUP_V1 archive orchestration."""

import time
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from xma.adapters.archive import RepositoryArchiveLock, SQLiteArchiveStore
from xma.application.download import DownloadService
from xma.domain.archive import ArchiveRequest, ArchiveRun, ArchiveStatus
from xma.domain.download import DownloadRequest
from xma.domain.errors import CatalogError, DiscoveryError, DomainError, DownloadError
from xma.domain.ports import IncrementalDiscoveryProvider

_STRATEGY = "RESCAN_DEDUP_V1"


class ArchiveService:
    def __init__(
        self,
        download: DownloadService,
        provider: IncrementalDiscoveryProvider,
        store: SQLiteArchiveStore,
        repository_lock: RepositoryArchiveLock,
        *,
        clock: Callable[[], datetime] | None = None,
        monotonic: Callable[[], float] | None = None,
        sleeper: Callable[[float], None] | None = None,
        run_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._download = download
        self._provider = provider
        self._store = store
        self._lock = repository_lock
        self._clock = clock or (lambda: datetime.now(UTC))
        self._monotonic = monotonic or time.monotonic
        self._sleep = sleeper or time.sleep
        self._run_id = run_id_factory or (lambda: str(uuid4()))

    def execute(
        self,
        request: ArchiveRequest,
        discovery_timeout: int,
        progress: Callable[[str], None],
    ) -> ArchiveRun:
        with self._lock:
            now = self._clock()
            current = self._store.latest()
            if (
                current is not None
                and current.target.casefold() != request.target.handle.casefold()
            ):
                self._persist_terminal(current, ArchiveStatus.FAILED, "TARGET_CONFLICT")
                raise DomainError("archive target conflicts with the durable checkpoint")
            try:
                verified_total = self._download.verified_total(request.target.handle)
            except DownloadError:
                if current is not None:
                    self._persist_terminal(current, ArchiveStatus.FAILED, "REPOSITORY_INCONSISTENT")
                raise
            if current is not None and request.requested_total < current.downloaded_total:
                self._persist_terminal(current, ArchiveStatus.FAILED, "TOTAL_REDUCTION")
                raise DomainError("archive total must not reduce durable progress")
            if current is None:
                current = ArchiveRun(
                    self._run_id(),
                    request.target.handle,
                    request.requested_total,
                    request.batch_size,
                    request.request_interval_seconds,
                    ArchiveStatus.PENDING,
                    verified_total,
                    verified_total,
                    0,
                    _STRATEGY,
                    now,
                    now,
                )
            else:
                if current.downloaded_total > verified_total:
                    failed = replace(
                        current,
                        status=ArchiveStatus.FAILED,
                        updated_at=now,
                        last_error_code="CHECKPOINT_AHEAD_OF_REPOSITORY",
                    )
                    self._store.put(failed)
                    raise DomainError("archive checkpoint is inconsistent with repository")
                if current.status is ArchiveStatus.RUNNING:
                    current = replace(
                        current,
                        status=ArchiveStatus.PAUSED,
                        updated_at=now,
                        last_error_code="INTERRUPTED_PREVIOUS_RUN",
                    )
                    self._store.put(current)
                current = replace(
                    current,
                    downloaded_total=verified_total,
                    existing_before=verified_total
                    if current.page_number == 0 and current.existing_before != verified_total
                    else current.existing_before,
                )
                current = replace(
                    current,
                    requested_total=max(current.requested_total, request.requested_total),
                    batch_size=request.batch_size,
                    request_interval_seconds=request.request_interval_seconds,
                )
            if (
                current.status is ArchiveStatus.COMPLETED
                and current.downloaded_total >= request.requested_total
            ):
                return current
            current = replace(
                current, status=ArchiveStatus.RUNNING, updated_at=now, last_error_code=None
            )
            self._store.put(current)
            try:
                first_page = True
                while current.downloaded_total < request.requested_total:
                    if (
                        first_page
                        and current.next_allowed_at is not None
                        and current.next_allowed_at > self._clock()
                    ):
                        self._sleep((current.next_allowed_at - self._clock()).total_seconds())
                    elif not first_page:
                        started = self._monotonic()
                        self._sleep(float(request.request_interval_seconds))
                        if self._monotonic() < started:
                            raise DomainError("archive monotonic clock moved backwards")
                    page_total = min(
                        request.requested_total, current.downloaded_total + request.batch_size
                    )
                    summary = self._download.execute_incremental(
                        DownloadRequest(request.target.handle, page_total),
                        self._provider,
                        discovery_timeout,
                        1,
                        progress,
                    )
                    if summary.total_after != page_total:
                        raise DownloadError("archive page did not reach its confirmed target")
                    page = current.page_number + 1
                    completed = summary.total_after >= request.requested_total
                    current = replace(
                        current,
                        status=ArchiveStatus.COMPLETED if completed else ArchiveStatus.RUNNING,
                        downloaded_total=summary.total_after,
                        page_number=page,
                        updated_at=self._clock(),
                        completed_at=self._clock() if completed else None,
                        next_allowed_at=None
                        if completed
                        else self._clock() + timedelta(seconds=request.request_interval_seconds),
                    )
                    self._store.put(current)
                    first_page = False
            except DiscoveryError as error:
                self._persist_terminal(current, ArchiveStatus.PAUSED, error.__class__.__name__)
                raise
            except KeyboardInterrupt:
                self._persist_terminal(current, ArchiveStatus.PAUSED, "INTERRUPTED")
                raise
            except InterruptedError:
                self._persist_terminal(current, ArchiveStatus.PAUSED, "INTERRUPTED")
                raise
            except (DownloadError, CatalogError, DomainError) as error:
                self._persist_terminal(current, ArchiveStatus.FAILED, error.__class__.__name__)
                raise
            except Exception:
                self._persist_terminal(current, ArchiveStatus.FAILED, "UNEXPECTED_FAILURE")
                raise
            return current

    def _persist_terminal(
        self, current: ArchiveRun, status: ArchiveStatus, error_code: str
    ) -> None:
        self._store.put(
            replace(
                current,
                status=status,
                updated_at=self._clock(),
                last_error_code=error_code,
            )
        )
