"""Durable RESCAN_DEDUP_V1 archive orchestration."""

import shutil
import time
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from xma.adapters.archive import RepositoryArchiveLock, SQLiteArchiveStore
from xma.application.download import DownloadService
from xma.domain.archive import (
    ArchiveMode,
    ArchiveRequest,
    ArchiveRun,
    ArchiveStatus,
    CompletionReason,
)
from xma.domain.download import DownloadRequest
from xma.domain.errors import (
    ArchiveUnexpectedError,
    CatalogError,
    DiscoveryError,
    DomainError,
    DownloadError,
    ProviderExhaustedError,
)
from xma.domain.ports import IncrementalDiscoveryProvider

_STRATEGY = "RESCAN_DEDUP_V2"


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
            if request.mode is ArchiveMode.ALL:
                current = self._prepare_all_run(request, current, now)
            elif current is not None and current.mode is ArchiveMode.ALL:
                current = None
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
            if (
                request.mode is ArchiveMode.ALL
                and request.max_items is not None
                and request.max_items < verified_total
            ):
                raise DomainError("archive max-items is below verified repository progress")
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
                    mode=request.mode,
                    max_items=request.max_items,
                    max_runtime_seconds=request.max_runtime_seconds,
                    min_free_space_bytes=request.min_free_space_bytes,
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
                    max_items=request.max_items,
                    max_runtime_seconds=request.max_runtime_seconds,
                    min_free_space_bytes=request.min_free_space_bytes,
                )
            if (
                current.status is ArchiveStatus.COMPLETED
                and current.downloaded_total >= request.requested_total
            ):
                return current
            if (
                request.mode is ArchiveMode.ALL
                and request.max_items is not None
                and request.max_items == verified_total
            ):
                current = replace(
                    current,
                    status=ArchiveStatus.PAUSED,
                    downloaded_total=verified_total,
                    completion_reason=CompletionReason.SAFETY_CAP_REACHED,
                    last_error_code=None,
                    updated_at=self._clock(),
                )
                self._store.put(current)
                return current
            current = replace(
                current, status=ArchiveStatus.RUNNING, updated_at=now, last_error_code=None
            )
            self._store.put(current)
            try:
                first_page = True
                started_monotonic = self._monotonic()
                while request.mode is ArchiveMode.ALL or (
                    current.downloaded_total < request.requested_total
                ):
                    if (
                        request.mode is ArchiveMode.ALL
                        and self._monotonic() - started_monotonic >= request.max_runtime_seconds
                    ):
                        current = self._pause(
                            current, CompletionReason.MAX_RUNTIME_REACHED, "MAX_RUNTIME_REACHED"
                        )
                        return current
                    if request.mode is ArchiveMode.ALL and (
                        shutil.disk_usage(self._store.database.parent).free
                        < request.min_free_space_bytes
                    ):
                        current = self._pause(
                            current, CompletionReason.LOW_DISK_SPACE, "LOW_DISK_SPACE"
                        )
                        return current
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
                    page_total = current.downloaded_total + request.batch_size
                    if request.mode is ArchiveMode.BOUNDED:
                        page_total = min(request.requested_total, page_total)
                    elif request.max_items is not None:
                        page_total = min(request.max_items, page_total)
                    try:
                        summary = self._download.execute_incremental(
                            DownloadRequest(
                                request.target.handle,
                                page_total,
                                archive_all=request.mode is ArchiveMode.ALL,
                            ),
                            self._provider,
                            discovery_timeout,
                            1,
                            progress,
                            500,
                        )
                    except ProviderExhaustedError:
                        if request.mode is ArchiveMode.ALL:
                            current = replace(
                                current,
                                status=ArchiveStatus.COMPLETED,
                                completion_reason=CompletionReason.PROVIDER_EXHAUSTED,
                                updated_at=self._clock(),
                                completed_at=self._clock(),
                                last_error_code=None,
                            )
                            self._store.put(current)
                            return current
                        raise
                    if summary.total_after != page_total:
                        raise DownloadError("archive page did not reach its confirmed target")
                    page = current.page_number + 1
                    completed = (
                        request.mode is ArchiveMode.BOUNDED
                        and summary.total_after >= request.requested_total
                    )
                    capped = (
                        request.mode is ArchiveMode.ALL
                        and request.max_items is not None
                        and summary.total_after >= request.max_items
                    )
                    current = replace(
                        current,
                        status=ArchiveStatus.COMPLETED
                        if completed
                        else ArchiveStatus.PAUSED
                        if capped
                        else ArchiveStatus.RUNNING,
                        downloaded_total=summary.total_after,
                        failed_total=current.failed_total + summary.failed_count,
                        page_number=page,
                        updated_at=self._clock(),
                        completed_at=self._clock() if completed else None,
                        completion_reason=CompletionReason.REQUESTED_TOTAL_REACHED
                        if completed
                        else CompletionReason.SAFETY_CAP_REACHED
                        if capped
                        else None,
                        next_allowed_at=None
                        if completed
                        else self._clock() + timedelta(seconds=request.request_interval_seconds),
                    )
                    self._store.put(current)
                    if capped:
                        return current
                    first_page = False
            except DiscoveryError as error:
                self._persist_terminal(
                    current,
                    ArchiveStatus.PAUSED,
                    error.__class__.__name__,
                    CompletionReason.PROVIDER_TRANSIENT,
                )
                raise
            except KeyboardInterrupt:
                self._persist_terminal(
                    current,
                    ArchiveStatus.PAUSED,
                    "INTERRUPTED",
                    CompletionReason.INTERRUPTED,
                )
                raise
            except InterruptedError:
                self._persist_terminal(
                    current,
                    ArchiveStatus.PAUSED,
                    "INTERRUPTED",
                    CompletionReason.INTERRUPTED,
                )
                raise
            except (DownloadError, CatalogError, DomainError) as error:
                self._persist_terminal(
                    current,
                    ArchiveStatus.FAILED,
                    error.__class__.__name__,
                    CompletionReason.FAILED,
                )
                raise
            except Exception as error:
                self._persist_terminal(
                    current,
                    ArchiveStatus.FAILED,
                    "UNEXPECTED_FAILURE",
                    CompletionReason.FAILED,
                )
                raise ArchiveUnexpectedError("archive failed unexpectedly") from error
            return current

    def _persist_terminal(
        self,
        current: ArchiveRun,
        status: ArchiveStatus,
        error_code: str,
        reason: CompletionReason | None = None,
    ) -> None:
        self._store.put(
            replace(
                current,
                status=status,
                updated_at=self._clock(),
                last_error_code=error_code,
                completion_reason=reason,
            )
        )

    def _pause(self, current: ArchiveRun, reason: CompletionReason, error_code: str) -> ArchiveRun:
        paused = replace(
            current,
            status=ArchiveStatus.PAUSED,
            completion_reason=reason,
            last_error_code=error_code,
            updated_at=self._clock(),
        )
        self._store.put(paused)
        return paused

    def _prepare_all_run(
        self, request: ArchiveRequest, current: ArchiveRun | None, now: datetime
    ) -> ArchiveRun | None:
        if current is None or current.mode is ArchiveMode.BOUNDED:
            if request.resume:
                raise DomainError("archive --resume requires a compatible paused ALL run")
            return None
        if current.target.casefold() != request.target.handle.casefold():
            raise DomainError("archive target conflicts with the durable checkpoint")
        if request.resume:
            if current.status is not ArchiveStatus.PAUSED:
                raise DomainError("archive --resume requires a compatible paused ALL run")
            return replace(current, resumed_at=now)
        if current.status is ArchiveStatus.PAUSED:
            raise DomainError("paused ALL run requires --resume")
        if current.status is ArchiveStatus.RUNNING:
            return current
        return None
