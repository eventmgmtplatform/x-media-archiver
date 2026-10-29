from datetime import UTC, datetime, timedelta, timezone

import pytest

from xma.domain.enums import DownloadStatus, MediaType, PostType, RunStatus
from xma.domain.errors import DomainError, InvalidIdentityError, InvalidTransitionError
from xma.domain.identity import media_identity, parse_media_identity
from xma.domain.models import (
    DOWNLOAD_TRANSITIONS,
    Artifact,
    DiscoveryRun,
    DownloadJob,
    MediaAsset,
    Post,
    Profile,
)

NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


def test_profile_normalizes_handle_and_timestamps() -> None:
    local = NOW.astimezone(timezone(timedelta(hours=-6)))
    profile = Profile("123", "@Example_1", "Example", local, local, local)
    assert profile.handle == "Example_1"
    assert profile.observed_at == NOW
    assert profile.observed_at.tzinfo is UTC


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"profile_id": "0"}, "positive decimal"),
        ({"handle": "bad-handle"}, "1-15"),
        ({"display_name": " "}, "must not be blank"),
        ({"observed_at": datetime(2026, 1, 1)}, "timezone-aware"),
    ],
)
def test_profile_rejects_invalid_fields(kwargs: dict[str, object], message: str) -> None:
    values: dict[str, object] = {
        "profile_id": "123",
        "handle": "example",
        "display_name": "Example",
        "observed_at": NOW,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(kwargs)
    with pytest.raises(DomainError, match=message):
        Profile(**values)  # type: ignore[arg-type]


def test_post_requires_stable_identity_and_canonical_url() -> None:
    post = Post("456", "123", "https://x.com/i/status/456", "text", NOW, PostType.POST)
    assert post.published_at is NOW
    with pytest.raises(DomainError, match="canonical_url"):
        Post("456", "123", "https://example.test/456", "", NOW, PostType.POST)
    with pytest.raises(InvalidIdentityError):
        Post("bad", "123", "https://x.com/i/status/bad", "", NOW, PostType.POST)


def test_media_identity_and_validation() -> None:
    asset = MediaAsset("456", 0, MediaType.VIDEO, 1000, 1920, 1080, ("source",))
    assert asset.asset_id == "456:0" == media_identity("456", 0)
    with pytest.raises(DomainError, match="non-negative"):
        MediaAsset("456", -1, MediaType.VIDEO)
    with pytest.raises(DomainError, match="blank"):
        MediaAsset("456", 0, MediaType.VIDEO, variants=("",))


@pytest.mark.parametrize("asset_id", [":", "bad:0", "1:-1", "1:x", "1:00", "1:0:0"])
def test_download_job_rejects_invalid_composite_asset_identity(asset_id: str) -> None:
    with pytest.raises(InvalidIdentityError, match="asset_id"):
        DownloadJob("job", asset_id, "run", DownloadStatus.QUEUED, 0, NOW, NOW)


def test_parse_media_identity_returns_validated_components() -> None:
    assert parse_media_identity("456:0") == ("456", 0)


def test_discovery_run_validates_lifecycle_and_counts() -> None:
    run = DiscoveryRun("run-1", "fixtures", NOW, RunStatus.RUNNING)
    assert run.finished_at is None
    with pytest.raises(DomainError, match="running"):
        DiscoveryRun("run-1", "fixtures", NOW, RunStatus.RUNNING, NOW)
    with pytest.raises(DomainError, match="precede"):
        DiscoveryRun("run-1", "fixtures", NOW, RunStatus.COMPLETED, NOW - timedelta(seconds=1))
    with pytest.raises(DomainError, match="non-negative"):
        DiscoveryRun("run-1", "fixtures", NOW, RunStatus.RUNNING, discovered_count=-1)
    with pytest.raises(DomainError, match="must not be blank"):
        DiscoveryRun("", "fixtures", NOW, RunStatus.RUNNING)


def _job(status: DownloadStatus = DownloadStatus.DISCOVERED) -> DownloadJob:
    error = (
        ("NETWORK", "temporary")
        if status in {DownloadStatus.FAILED_RETRYABLE, DownloadStatus.FAILED_FINAL}
        else (None, None)
    )
    return DownloadJob("job-1", "456:0", "run-1", status, 0, NOW, NOW, *error)


@pytest.mark.parametrize(
    ("source", "targets"),
    [(source, targets) for source, targets in DOWNLOAD_TRANSITIONS.items()],
)
def test_download_transition_matrix(
    source: DownloadStatus, targets: frozenset[DownloadStatus]
) -> None:
    for target in DownloadStatus:
        if target in targets:
            error = (
                {"error_code": "IO", "error_message": "temporary"}
                if target in {DownloadStatus.FAILED_RETRYABLE, DownloadStatus.FAILED_FINAL}
                else {}
            )
            transitioned = _job(source).transition(target, NOW + timedelta(seconds=1), **error)
            assert transitioned.status is target
            assert transitioned.attempts == (1 if target is DownloadStatus.DOWNLOADING else 0)
        else:
            with pytest.raises(InvalidTransitionError):
                _job(source).transition(target, NOW + timedelta(seconds=1))


def test_download_job_rejects_invalid_errors_and_time() -> None:
    with pytest.raises(DomainError, match="must be valid"):
        DownloadJob("", "invalid", "run", DownloadStatus.QUEUED, 0, NOW, NOW)
    with pytest.raises(DomainError, match="required only"):
        DownloadJob("job", "456:0", "run", DownloadStatus.FAILED_FINAL, 1, NOW, NOW)
    with pytest.raises(DomainError, match="required only"):
        DownloadJob("job", "456:0", "run", DownloadStatus.QUEUED, 0, NOW, NOW, "X", "bad")
    with pytest.raises(DomainError, match="precede"):
        DownloadJob(
            "job", "456:0", "run", DownloadStatus.QUEUED, 0, NOW, NOW - timedelta(seconds=1)
        )


def test_artifact_normalizes_hash_and_rejects_unsafe_paths() -> None:
    artifact = Artifact(
        "artifact-1", "job-1", "profiles/a/media.mp4", "video/mp4", 12, "A" * 64, NOW
    )
    assert artifact.sha256 == "a" * 64
    for path in ("/tmp/file", "../file", "safe/../file", "", ".", "safe//file"):
        with pytest.raises(DomainError, match="relative POSIX"):
            Artifact("artifact-1", "job-1", path, "video/mp4", 12, "a" * 64, NOW)
    with pytest.raises(DomainError, match="64 hexadecimal"):
        Artifact("artifact-1", "job-1", "safe/file", "video/mp4", 12, "bad", NOW)
    with pytest.raises(DomainError, match="media type"):
        Artifact("artifact-1", "job-1", "safe/file", "invalid", 12, "a" * 64, NOW)
    with pytest.raises(DomainError, match="must not be blank"):
        Artifact("", "job-1", "safe/file", "video/mp4", 12, "a" * 64, NOW)
