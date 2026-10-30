"""Typed, privacy-preserving execution reports for CLI rendering."""

from dataclasses import dataclass, replace
from pathlib import PurePosixPath
from typing import Any

from xma.domain.archive import ArchiveMode, ArchiveRun, CompletionReason
from xma.domain.discovery import DiscoveryTargetKind, normalize_discovery_target
from xma.domain.download import DownloadSummary

REPORT_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class AccountReport:
    handle: str | None
    display_name: str | None = None
    target_kind: str | None = None

    def public_dict(self) -> dict[str, object]:
        return {
            "handle": self.handle,
            "display_name": self.display_name,
            "target_kind": self.target_kind,
        }


@dataclass(frozen=True, slots=True)
class RequestReport:
    mode: str
    requested: int | None
    quality: str = "provider-best"

    def public_dict(self) -> dict[str, object]:
        return {"mode": self.mode, "requested": self.requested, "quality": self.quality}


@dataclass(frozen=True, slots=True)
class CountsReport:
    existing_before: int | None
    downloaded_this_run: int | None
    skipped: int | None
    failed: int | None
    total_after: int | None

    def public_dict(self) -> dict[str, object]:
        return {
            "existing_before": self.existing_before,
            "downloaded_this_run": self.downloaded_this_run,
            "skipped": self.skipped,
            "failed": self.failed,
            "total_after": self.total_after,
        }


@dataclass(frozen=True, slots=True)
class CheckpointReport:
    page: int | None
    remaining: int | None
    resumable: bool

    def public_dict(self) -> dict[str, object]:
        return {"page": self.page, "remaining": self.remaining, "resumable": self.resumable}


@dataclass(frozen=True, slots=True)
class VideoReport:
    post_id: str
    media_index: int
    published_at: str | None
    duration_ms: int | None
    width: int | None
    height: int | None
    media_type: str | None
    mime_type: str
    extension: str
    quality: str
    size_bytes: int
    sha256: str
    relative_path: str
    job_status: str

    def public_dict(self) -> dict[str, object]:
        return {
            "post_id": self.post_id,
            "media_index": self.media_index,
            "published_at": self.published_at,
            "duration_ms": self.duration_ms,
            "width": self.width,
            "height": self.height,
            "resolution": None
            if self.width is None or self.height is None
            else f"{self.width}x{self.height}",
            "media_type": self.media_type,
            "mime_type": self.mime_type,
            "extension": self.extension,
            "quality": self.quality,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "relative_path": self.relative_path,
            "job_status": self.job_status,
        }


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    command: str
    account: AccountReport
    request: RequestReport | None
    status: str
    counts: CountsReport
    checkpoint: CheckpointReport | None
    reason: str | None
    video: VideoReport | None = None
    complete: bool | None = None
    provider_exhausted: bool = False
    goal: str | None = None
    operational_cap: int | None = None
    elapsed_seconds: float | None = None
    error_code: str | None = None
    exit_code: int | None = None
    progress_available: bool = True

    def public_dict(self) -> dict[str, object]:
        return {
            "report_schema_version": REPORT_SCHEMA_VERSION,
            "command": self.command,
            "account": self.account.public_dict(),
            "request": None if self.request is None else self.request.public_dict(),
            "status": self.status,
            "counts": self.counts.public_dict(),
            "checkpoint": None if self.checkpoint is None else self.checkpoint.public_dict(),
            "reason": self.reason,
            "video": None if self.video is None else self.video.public_dict(),
            "complete": self.complete,
            "provider_exhausted": self.provider_exhausted,
            "goal": self.goal,
            "operational_cap": self.operational_cap,
            "elapsed_seconds": self.elapsed_seconds,
            "error_code": self.error_code,
            "exit_code": self.exit_code,
            "progress_available": self.progress_available,
        }


def download_report(
    summary: DownloadSummary,
    *,
    mode: str,
    requested: int,
) -> ExecutionReport:
    target = normalize_discovery_target(summary.target)
    video = _new_video(summary)
    return ExecutionReport(
        command="download",
        account=AccountReport(target.handle, target_kind=target.kind.value),
        request=RequestReport(mode, requested),
        status="COMPLETED" if summary.complete else "PAUSED",
        counts=CountsReport(
            summary.existing_before,
            summary.downloaded_count,
            summary.skipped_count,
            summary.failed_count,
            summary.total_after,
        ),
        checkpoint=CheckpointReport(
            None, max(0, summary.requested_limit - summary.total_after), False
        ),
        reason="PROVIDER_EXHAUSTED" if summary.provider_exhausted else None,
        video=video,
        complete=summary.complete,
        provider_exhausted=summary.provider_exhausted,
    )


def archive_report(run: ArchiveRun, *, command: str = "archive") -> ExecutionReport:
    values = run.public_dict()
    is_all = run.mode is ArchiveMode.ALL
    return ExecutionReport(
        command=command,
        account=AccountReport(run.target, target_kind=DiscoveryTargetKind.PROFILE.value),
        request=RequestReport(run.mode.value, None if is_all else run.requested_total),
        status=run.status.value,
        counts=CountsReport(
            run.existing_before,
            max(0, run.downloaded_total - run.existing_before),
            0,
            run.failed_total,
            run.downloaded_total,
        ),
        checkpoint=CheckpointReport(
            run.page_number,
            None if is_all else run.remaining,
            bool(values["resumable"]),
        ),
        reason=None if run.completion_reason is None else run.completion_reason.value,
        complete=bool(values["complete"]),
        provider_exhausted=run.completion_reason is CompletionReason.PROVIDER_EXHAUSTED,
        goal=str(values["goal"]),
        operational_cap=run.max_items if is_all else None,
        elapsed_seconds=max(
            0.0,
            (run.updated_at - (run.resumed_at or run.created_at)).total_seconds(),
        ),
        error_code=run.last_error_code,
    )


def failure_report(
    *,
    command: str,
    handle: str | None,
    error_code: str,
    exit_code: int,
    run: ArchiveRun | None = None,
    progress: dict[str, Any] | None = None,
) -> ExecutionReport:
    if run is not None:
        report = archive_report(run, command=command)
        return replace(report, error_code=error_code, exit_code=exit_code)
    progress = progress or {}
    return ExecutionReport(
        command=command,
        account=AccountReport(handle),
        request=None,
        status="FAILED",
        counts=CountsReport(
            progress.get("existing_before"),
            progress.get("downloaded_this_run"),
            progress.get("skipped_count"),
            progress.get("failed_count"),
            progress.get("total_after"),
        ),
        checkpoint=None,
        reason=error_code,
        error_code=error_code,
        exit_code=exit_code,
        progress_available=bool(progress),
    )


def _new_video(summary: DownloadSummary) -> VideoReport | None:
    if summary.downloaded_count != 1 or not summary.artifacts:
        return None
    artifact = summary.artifacts[-1]
    try:
        relative = str(artifact["relative_path"])
        if PurePosixPath(relative).is_absolute() or ".." in PurePosixPath(relative).parts:
            return None
        asset_id = str(artifact["asset_id"])
        post_id, media_index_text = asset_id.split(":", 1)
        media_index = _integer(artifact.get("media_index", media_index_text))
        size = _integer(artifact["size_bytes"])
        width = artifact.get("width")
        height = artifact.get("height")
        duration = artifact.get("duration_ms")
        return VideoReport(
            post_id=str(artifact.get("post_id") or post_id),
            media_index=media_index,
            published_at=_optional_string(artifact.get("published_at")),
            duration_ms=None if duration is None else _integer(duration),
            width=None if width is None else _integer(width),
            height=None if height is None else _integer(height),
            media_type=_optional_string(artifact.get("media_type")),
            mime_type=str(artifact["mime_type"]),
            extension=str(artifact["extension"]),
            quality=str(artifact.get("quality_policy", "provider-best")),
            size_bytes=size,
            sha256=str(artifact["sha256"]),
            relative_path=relative,
            job_status=str(artifact.get("job_status") or "COMPLETED"),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _integer(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError("report value is not an integer")
    return int(value)
