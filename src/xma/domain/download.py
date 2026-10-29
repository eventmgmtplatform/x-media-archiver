"""Typed values for the bounded B04 download vertical slice."""

from dataclasses import dataclass

from xma.domain.errors import DomainError
from xma.domain.identity import validate_non_negative, validate_sha256


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    target: str
    limit: int

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise DomainError("download target must not be blank")
        if not 1 <= self.limit <= 5:
            raise DomainError("download limit must be between 1 and 5")


@dataclass(frozen=True, slots=True)
class DownloadedArtifact:
    mime_type: str
    size_bytes: int
    sha256: str
    extension: str

    def __post_init__(self) -> None:
        if not self.mime_type.startswith(("video/", "audio/")):
            raise DomainError("downloaded content must be audiovisual")
        validate_non_negative(self.size_bytes, "size_bytes")
        if self.size_bytes == 0:
            raise DomainError("downloaded content must not be empty")
        object.__setattr__(self, "sha256", validate_sha256(self.sha256))
        if (
            not self.extension.startswith(".")
            or len(self.extension) > 10
            or not self.extension[1:].isalnum()
        ):
            raise DomainError("download extension is invalid")


@dataclass(frozen=True, slots=True)
class DownloadSummary:
    target: str
    requested_limit: int
    downloaded_count: int
    skipped_count: int
    failed_count: int
    run_id: str
    artifacts: tuple[dict[str, object], ...]

    def public_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "requested_limit": self.requested_limit,
            "downloaded_count": self.downloaded_count,
            "skipped_count": self.skipped_count,
            "failed_count": self.failed_count,
            "run_id": self.run_id,
            "artifacts": list(self.artifacts),
        }
