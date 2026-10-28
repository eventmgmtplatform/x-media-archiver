"""Validation and normalization for stable catalog identities."""

import re
from datetime import UTC, datetime
from pathlib import PurePosixPath

from xma.domain.errors import DomainError, InvalidIdentityError

_X_ID = re.compile(r"^[1-9][0-9]*$")
_HANDLE = re.compile(r"^[A-Za-z0-9_]{1,15}$")
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def validate_x_id(value: str, field: str) -> str:
    if not _X_ID.fullmatch(value):
        raise InvalidIdentityError(f"{field} must be a positive decimal X ID")
    return value


def normalize_handle(value: str) -> str:
    handle = value.removeprefix("@")
    if not _HANDLE.fullmatch(handle):
        raise InvalidIdentityError("handle must contain 1-15 letters, numbers, or underscores")
    return handle


def utc_datetime(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


def validate_non_negative(value: int, field: str) -> int:
    if value < 0:
        raise DomainError(f"{field} must be non-negative")
    return value


def validate_sha256(value: str) -> str:
    if not _SHA256.fullmatch(value):
        raise DomainError("sha256 must contain exactly 64 hexadecimal characters")
    return value.lower()


def validate_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise DomainError("artifact path must be a normalized relative POSIX path")
    normalized = path.as_posix()
    if normalized != value or value.startswith("/"):
        raise DomainError("artifact path must be a normalized relative POSIX path")
    return normalized


def media_identity(post_id: str, media_index: int) -> str:
    return (
        f"{validate_x_id(post_id, 'post_id')}:{validate_non_negative(media_index, 'media_index')}"
    )
