"""Finite domain state sets."""

from enum import StrEnum


class PostType(StrEnum):
    POST = "POST"
    REPLY = "REPLY"
    REPOST = "REPOST"
    QUOTE = "QUOTE"


class MediaType(StrEnum):
    VIDEO = "VIDEO"
    ANIMATED_GIF = "ANIMATED_GIF"
    BROADCAST = "BROADCAST"
    SPACE = "SPACE"


class RunStatus(StrEnum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DownloadStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    COMPLETED = "COMPLETED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_FINAL = "FAILED_FINAL"
    SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
    RESTRICTED = "RESTRICTED"
