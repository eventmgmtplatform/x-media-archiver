"""Offline execution-report contract tests."""

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from xma.application.reporting import archive_report, download_report, failure_report
from xma.domain.archive import ArchiveMode, ArchiveRun, ArchiveStatus, CompletionReason
from xma.domain.download import DownloadSummary

NOW = datetime(2026, 10, 30, tzinfo=UTC)


def artifact(post_id: str, *, path: str | None = None) -> dict[str, object]:
    return {
        "asset_id": f"{post_id}:0",
        "post_id": post_id,
        "media_index": 0,
        "published_at": NOW.isoformat(),
        "duration_ms": 291000,
        "width": 1920,
        "height": 1080,
        "media_type": "VIDEO",
        "mime_type": "video/mp4",
        "extension": ".mp4",
        "quality_policy": "provider-best",
        "size_bytes": 220200960,
        "sha256": "a" * 64,
        "relative_path": path or f"profiles/example/posts/{post_id}/0/video.mp4",
        "job_status": "COMPLETED",
    }


def summary(
    *, downloaded: int, existing: int, artifacts: tuple[dict[str, object], ...]
) -> DownloadSummary:
    total = existing + downloaded
    return DownloadSummary(
        "@example",
        total or 1,
        downloaded,
        0,
        0,
        "run",
        artifacts,
        existing,
        total,
        True,
    )


def run(
    *,
    mode: ArchiveMode = ArchiveMode.BOUNDED,
    status: ArchiveStatus = ArchiveStatus.COMPLETED,
    reason: CompletionReason | None = CompletionReason.REQUESTED_TOTAL_REACHED,
    total: int = 10,
) -> ArchiveRun:
    return ArchiveRun(
        "run",
        "example",
        10,
        2,
        1,
        status,
        5,
        total,
        3,
        "RESCAN_DEDUP_V2",
        NOW,
        NOW + timedelta(seconds=4),
        NOW + timedelta(seconds=4) if status is ArchiveStatus.COMPLETED else None,
        mode=mode,
        completion_reason=reason,
        max_items=20 if mode is ArchiveMode.ALL else None,
    )


def test_single_new_video_report_identifies_new_artifact() -> None:
    old = artifact("100")
    new = artifact("200")
    report: Any = download_report(
        summary(downloaded=1, existing=1, artifacts=(old, new)), mode="ADD", requested=1
    ).public_dict()
    assert report["report_schema_version"] == 1
    assert report["account"] == {
        "handle": "example",
        "display_name": None,
        "target_kind": "PROFILE",
    }
    assert report["counts"]["downloaded_this_run"] == 1
    assert report["video"]["post_id"] == "200"
    assert report["video"]["resolution"] == "1920x1080"
    assert report["video"]["relative_path"].startswith("profiles/")


@pytest.mark.parametrize("downloaded", [0, 2, 5])
def test_report_is_compact_unless_exactly_one_video_is_new(downloaded: int) -> None:
    artifacts = tuple(artifact(str(index)) for index in range(max(downloaded, 1)))
    report: Any = download_report(
        summary(downloaded=downloaded, existing=1, artifacts=artifacts),
        mode="LIMIT",
        requested=max(downloaded, 1),
    ).public_dict()
    assert report["video"] is None
    assert report["counts"]["downloaded_this_run"] == downloaded


def test_single_video_detail_fails_closed_for_unsafe_path() -> None:
    report = download_report(
        summary(downloaded=1, existing=0, artifacts=(artifact("200", path="/private/video.mp4"),)),
        mode="LIMIT",
        requested=1,
    )
    assert report.video is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (run(), ("BOUNDED", True, False, 0)),
        (
            run(
                mode=ArchiveMode.ALL,
                status=ArchiveStatus.PAUSED,
                reason=CompletionReason.SAFETY_CAP_REACHED,
            ),
            ("ALL", False, False, None),
        ),
        (
            run(mode=ArchiveMode.ALL, reason=CompletionReason.PROVIDER_EXHAUSTED),
            ("ALL", True, True, None),
        ),
    ],
)
def test_archive_report_modes(value: ArchiveRun, expected: tuple[object, ...]) -> None:
    report: Any = archive_report(value).public_dict()
    assert (
        report["request"]["mode"],
        report["complete"],
        report["provider_exhausted"],
        report["checkpoint"]["remaining"],
    ) == expected
    assert report["counts"]["downloaded_this_run"] == 5
    assert report["elapsed_seconds"] == 4.0


def test_terminal_all_noop_and_status_are_offline_equivalent() -> None:
    value = replace(
        run(mode=ArchiveMode.ALL, reason=CompletionReason.PROVIDER_EXHAUSTED),
        existing_before=10,
        downloaded_total=10,
    )
    archived: Any = archive_report(value).public_dict()
    status: Any = archive_report(value, command="status").public_dict()
    assert archived["counts"]["downloaded_this_run"] == 0
    assert status["counts"] == archived["counts"]
    assert status["command"] == "status"


def test_failure_report_does_not_invent_progress_or_leak_sensitive_data() -> None:
    report: Any = failure_report(
        command="download",
        handle="example",
        error_code="DOWNLOAD_FAILED",
        exit_code=9,
    ).public_dict()
    encoded = json.dumps(report, sort_keys=True)
    assert report["progress_available"] is False
    assert set(report["counts"].values()) == {None}
    assert report["exit_code"] == 9
    for marker in ("auth_token", "ct0", "cookies.sqlite", "Traceback", "/home/"):
        assert marker not in encoded


def test_failure_report_uses_durable_archive_progress() -> None:
    value = replace(
        run(mode=ArchiveMode.ALL, status=ArchiveStatus.FAILED, reason=None),
        last_error_code="UNEXPECTED_FAILURE",
    )
    report: Any = failure_report(
        command="archive",
        handle="example",
        error_code="UNEXPECTED_FAILURE",
        exit_code=5,
        run=value,
    ).public_dict()
    assert report["status"] == "FAILED"
    assert report["counts"]["total_after"] == 10
    assert report["checkpoint"]["page"] == 3
    assert report["error_code"] == "UNEXPECTED_FAILURE"
    assert report["exit_code"] == 5
