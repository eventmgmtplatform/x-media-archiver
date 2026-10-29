"""Immutable domain aggregates stored by the catalog."""

from dataclasses import dataclass, field, replace
from datetime import datetime

from xma.domain.enums import DownloadStatus, MediaType, PostType, RunStatus
from xma.domain.errors import DomainError, InvalidTransitionError
from xma.domain.identity import (
    media_identity,
    normalize_handle,
    parse_media_identity,
    utc_datetime,
    validate_non_negative,
    validate_relative_path,
    validate_sha256,
    validate_x_id,
)


@dataclass(frozen=True, slots=True)
class Profile:
    profile_id: str
    handle: str
    display_name: str
    observed_at: datetime
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", validate_x_id(self.profile_id, "profile_id"))
        object.__setattr__(self, "handle", normalize_handle(self.handle))
        if not self.display_name.strip():
            raise DomainError("display_name must not be blank")
        for name in ("observed_at", "created_at", "updated_at"):
            object.__setattr__(self, name, utc_datetime(getattr(self, name), name))


@dataclass(frozen=True, slots=True)
class Post:
    post_id: str
    author_profile_id: str
    canonical_url: str
    text: str
    published_at: datetime
    post_type: PostType

    def __post_init__(self) -> None:
        object.__setattr__(self, "post_id", validate_x_id(self.post_id, "post_id"))
        object.__setattr__(
            self, "author_profile_id", validate_x_id(self.author_profile_id, "author_profile_id")
        )
        expected = f"https://x.com/i/status/{self.post_id}"
        if self.canonical_url != expected:
            raise DomainError(f"canonical_url must be {expected}")
        object.__setattr__(self, "published_at", utc_datetime(self.published_at, "published_at"))


@dataclass(frozen=True, slots=True)
class MediaAsset:
    post_id: str
    media_index: int
    media_type: MediaType
    duration_ms: int | None = None
    width: int | None = None
    height: int | None = None
    variants: tuple[str, ...] = ()
    asset_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "asset_id", media_identity(self.post_id, self.media_index))
        for name in ("duration_ms", "width", "height"):
            value = getattr(self, name)
            if value is not None:
                validate_non_negative(value, name)
        if any(not variant.strip() for variant in self.variants):
            raise DomainError("variants must not contain blank values")


@dataclass(frozen=True, slots=True)
class DiscoveryRun:
    run_id: str
    strategy: str
    started_at: datetime
    status: RunStatus
    finished_at: datetime | None = None
    cursor: str | None = None
    discovered_count: int = 0
    error_count: int = 0

    def __post_init__(self) -> None:
        if not self.run_id.strip() or not self.strategy.strip():
            raise DomainError("run_id and strategy must not be blank")
        object.__setattr__(self, "started_at", utc_datetime(self.started_at, "started_at"))
        if self.finished_at is not None:
            finished = utc_datetime(self.finished_at, "finished_at")
            if finished < self.started_at:
                raise DomainError("finished_at must not precede started_at")
            object.__setattr__(self, "finished_at", finished)
        if self.status is RunStatus.RUNNING and self.finished_at is not None:
            raise DomainError("a running discovery cannot have finished_at")
        for name in ("discovered_count", "error_count"):
            validate_non_negative(getattr(self, name), name)


DOWNLOAD_TRANSITIONS: dict[DownloadStatus, frozenset[DownloadStatus]] = {
    DownloadStatus.DISCOVERED: frozenset(
        {DownloadStatus.QUEUED, DownloadStatus.SKIPPED_DUPLICATE, DownloadStatus.RESTRICTED}
    ),
    DownloadStatus.QUEUED: frozenset({DownloadStatus.DOWNLOADING, DownloadStatus.RESTRICTED}),
    DownloadStatus.DOWNLOADING: frozenset(
        {DownloadStatus.COMPLETED, DownloadStatus.FAILED_RETRYABLE, DownloadStatus.FAILED_FINAL}
    ),
    DownloadStatus.FAILED_RETRYABLE: frozenset(
        {DownloadStatus.QUEUED, DownloadStatus.FAILED_FINAL}
    ),
    DownloadStatus.COMPLETED: frozenset(),
    DownloadStatus.FAILED_FINAL: frozenset({DownloadStatus.QUEUED}),
    DownloadStatus.SKIPPED_DUPLICATE: frozenset(),
    DownloadStatus.RESTRICTED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class DownloadJob:
    job_id: str
    asset_id: str
    run_id: str
    status: DownloadStatus
    attempts: int
    created_at: datetime
    updated_at: datetime
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.job_id.strip() or not self.run_id.strip():
            raise DomainError("job_id and run_id must be valid non-blank values")
        parse_media_identity(self.asset_id)
        validate_non_negative(self.attempts, "attempts")
        object.__setattr__(self, "created_at", utc_datetime(self.created_at, "created_at"))
        object.__setattr__(self, "updated_at", utc_datetime(self.updated_at, "updated_at"))
        if self.updated_at < self.created_at:
            raise DomainError("updated_at must not precede created_at")
        has_error = self.error_code is not None or self.error_message is not None
        is_failure = self.status in {DownloadStatus.FAILED_RETRYABLE, DownloadStatus.FAILED_FINAL}
        if has_error != is_failure or (
            is_failure and (not self.error_code or not self.error_message)
        ):
            raise DomainError("normalized error code and message are required only for failed jobs")

    def transition(
        self,
        status: DownloadStatus,
        at: datetime,
        *,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> "DownloadJob":
        if status not in DOWNLOAD_TRANSITIONS[self.status]:
            raise InvalidTransitionError(f"cannot transition {self.status} to {status}")
        attempts = self.attempts + (status is DownloadStatus.DOWNLOADING)
        return replace(
            self,
            status=status,
            attempts=attempts,
            updated_at=at,
            error_code=error_code,
            error_message=error_message,
        )

    def retry(self, at: datetime) -> "DownloadJob":
        """Start an explicit governed retry while preserving the attempt counter."""
        if self.status is not DownloadStatus.FAILED_FINAL:
            raise InvalidTransitionError("only a final failed job can be retried")
        return replace(
            self,
            status=DownloadStatus.QUEUED,
            updated_at=at,
            error_code=None,
            error_message=None,
        )


@dataclass(frozen=True, slots=True)
class Artifact:
    artifact_id: str
    job_id: str
    relative_path: str
    mime_type: str
    size_bytes: int
    sha256: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.artifact_id.strip() or not self.job_id.strip():
            raise DomainError("artifact_id and job_id must not be blank")
        object.__setattr__(self, "relative_path", validate_relative_path(self.relative_path))
        if "/" not in self.mime_type or any(char.isspace() for char in self.mime_type):
            raise DomainError("mime_type must be a valid media type")
        validate_non_negative(self.size_bytes, "size_bytes")
        object.__setattr__(self, "sha256", validate_sha256(self.sha256))
        object.__setattr__(self, "created_at", utc_datetime(self.created_at, "created_at"))
