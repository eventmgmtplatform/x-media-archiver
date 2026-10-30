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


@dataclass(frozen=True, slots=True)
class ArchiveRequest:
    target: DiscoveryTarget
    requested_total: int
    batch_size: int
    request_interval_seconds: int

    @classmethod
    def create(cls, target: str, total: int, batch: int, interval: int) -> "ArchiveRequest":
        normalized = normalize_discovery_target(target)
        if normalized.kind is not DiscoveryTargetKind.PROFILE:
            raise DomainError("archive accepts profile targets only")
        return cls(normalized, total, batch, interval)

    def __post_init__(self) -> None:
        if self.target.kind is not DiscoveryTargetKind.PROFILE:
            raise DomainError("archive accepts profile targets only")
        if not 1 <= self.requested_total <= 20:
            raise DomainError("archive limit must be between 1 and 20")
        if not 1 <= self.batch_size <= 5:
            raise DomainError("archive batch size must be between 1 and 5")
        if not 1 <= self.request_interval_seconds <= 60:
            raise DomainError("archive request interval must be between 1 and 60 seconds")


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

    @property
    def remaining(self) -> int:
        return max(0, self.requested_total - self.downloaded_total)

    def public_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "target": self.target,
            "status": self.status.value,
            "requested_total": self.requested_total,
            "existing_before": self.existing_before,
            "downloaded_total": self.downloaded_total,
            "remaining": self.remaining,
            "page_number": self.page_number,
            "checkpoint_strategy": self.checkpoint_strategy,
            "last_error_code": self.last_error_code,
            "updated_at": self.updated_at.isoformat(),
            "complete": self.status is ArchiveStatus.COMPLETED,
        }
