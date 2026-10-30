"""Durable B05 archive request and status values."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from xma.domain.discovery import DiscoveryTarget, DiscoveryTargetKind, normalize_discovery_target
from xma.domain.errors import DomainError


class ArchiveStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ArchiveMode(StrEnum):
    BOUNDED = "BOUNDED"
    ALL = "ALL"


class CompletionReason(StrEnum):
    REQUESTED_TOTAL_REACHED = "REQUESTED_TOTAL_REACHED"
    PROVIDER_EXHAUSTED = "PROVIDER_EXHAUSTED"
    SAFETY_CAP_REACHED = "SAFETY_CAP_REACHED"
    MAX_RUNTIME_REACHED = "MAX_RUNTIME_REACHED"
    LOW_DISK_SPACE = "LOW_DISK_SPACE"
    INTERRUPTED = "INTERRUPTED"
    PROVIDER_TRANSIENT = "PROVIDER_TRANSIENT"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ArchiveRequest:
    target: DiscoveryTarget
    requested_total: int
    batch_size: int
    request_interval_seconds: int
    mode: ArchiveMode = ArchiveMode.BOUNDED
    max_items: int | None = None
    max_runtime_seconds: int = 3600
    min_free_space_bytes: int = 10 * 1024**3
    resume: bool = False

    @classmethod
    def create(cls, target: str, total: int, batch: int, interval: int) -> "ArchiveRequest":
        normalized = normalize_discovery_target(target)
        if normalized.kind is not DiscoveryTargetKind.PROFILE:
            raise DomainError("archive accepts profile targets only")
        return cls(normalized, total, batch, interval)

    @classmethod
    def create_all(
        cls,
        target: str,
        batch: int,
        interval: int,
        *,
        max_items: int | None = None,
        max_runtime_seconds: int = 3600,
        min_free_space_gib: int = 10,
        resume: bool = False,
    ) -> "ArchiveRequest":
        normalized = normalize_discovery_target(target)
        if normalized.kind is not DiscoveryTargetKind.PROFILE:
            raise DomainError("archive --all accepts profile targets only")
        return cls(
            normalized,
            max_items or 1,
            batch,
            interval,
            ArchiveMode.ALL,
            max_items,
            max_runtime_seconds,
            min_free_space_gib * 1024**3,
            resume,
        )

    def __post_init__(self) -> None:
        if self.target.kind is not DiscoveryTargetKind.PROFILE:
            raise DomainError("archive accepts profile targets only")
        if self.mode is ArchiveMode.BOUNDED and not 1 <= self.requested_total <= 20:
            raise DomainError("archive limit must be between 1 and 20")
        if self.mode is ArchiveMode.ALL and self.max_items is not None and self.max_items < 1:
            raise DomainError("archive max-items must be positive")
        if not 1 <= self.batch_size <= 20:
            raise DomainError("archive batch size must be between 1 and 20")
        if not 1 <= self.request_interval_seconds <= 60:
            raise DomainError("archive request interval must be between 1 and 60 seconds")
        if not 60 <= self.max_runtime_seconds <= 21600:
            raise DomainError("archive max runtime must be between 60 and 21600 seconds")
        if not 5 * 1024**3 <= self.min_free_space_bytes <= 1024 * 1024**3:
            raise DomainError("archive minimum free space must be between 5 and 1024 GiB")
        if self.resume and self.mode is not ArchiveMode.ALL:
            raise DomainError("archive --resume requires --all")


@dataclass(frozen=True, slots=True)
class ArchiveRun:
    run_id: str
    target: str
    requested_total: int
    batch_size: int
    request_interval_seconds: int
    status: ArchiveStatus
    existing_before: int
    downloaded_total: int
    page_number: int
    checkpoint_strategy: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    last_error_code: str | None = None
    next_allowed_at: datetime | None = None
    mode: ArchiveMode = ArchiveMode.BOUNDED
    completion_reason: CompletionReason | None = None
    failed_total: int = 0
    max_items: int | None = None
    max_runtime_seconds: int = 3600
    min_free_space_bytes: int = 10 * 1024**3
    resumed_at: datetime | None = None

    @property
    def remaining(self) -> int:
        return max(0, self.requested_total - self.downloaded_total)

    def public_dict(self) -> dict[str, object]:
        is_all = self.mode is ArchiveMode.ALL
        complete = self.status is ArchiveStatus.COMPLETED and (
            not is_all or self.completion_reason is CompletionReason.PROVIDER_EXHAUSTED
        )
        return {
            "run_id": self.run_id,
            "target": self.target,
            "status": self.status.value,
            "requested_total": None if is_all else self.requested_total,
            "existing_before": self.existing_before,
            "downloaded_total": self.downloaded_total,
            "remaining": None if is_all else self.remaining,
            "page_number": self.page_number,
            "checkpoint_strategy": self.checkpoint_strategy,
            "last_error_code": self.last_error_code,
            "updated_at": self.updated_at.isoformat(),
            "complete": complete,
            "mode": self.mode.value,
            "completion_reason": None
            if self.completion_reason is None
            else self.completion_reason.value,
            "failed_total": self.failed_total,
            "verified_total": self.downloaded_total,
            "checkpoint": self.page_number,
            "max_items": self.max_items,
            "max_runtime_seconds": self.max_runtime_seconds,
            "min_free_space_bytes": self.min_free_space_bytes,
            "elapsed_seconds": max(
                0.0, (self.updated_at - (self.resumed_at or self.created_at)).total_seconds()
            ),
            "resumable": self.mode is ArchiveMode.ALL and self.status is ArchiveStatus.PAUSED,
            "goal": "PROVIDER_EXHAUSTION" if is_all else "REQUESTED_TOTAL",
            "operational_cap": self.max_items if is_all else None,
        }
