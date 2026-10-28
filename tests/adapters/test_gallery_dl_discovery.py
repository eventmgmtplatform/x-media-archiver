import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from gallery_dl import config, exception  # type: ignore[import-untyped]

from xma.adapters.discovery.gallery_dl import (
    GalleryDlDiscoveryProvider,
    GalleryDlExtraction,
    _classified_error,
    _LimitedDataJob,
    _run_gallery_dl,
    map_gallery_dl_extraction,
)
from xma.domain.discovery import normalize_discovery_target
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import (
    DiscoveryContractError,
    DiscoveryError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
)

NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)
FIXTURE = Path(__file__).parents[1] / "fixtures/gallery_dl/twitter_videos.json"


def extraction() -> GalleryDlExtraction:
    payload: dict[str, Any] = json.loads(FIXTURE.read_text())
    return GalleryDlExtraction(
        payload["profile_record"], tuple(payload["media_records"]), tuple(payload["warnings"])
    )


def test_maps_fixture_and_applies_video_limit() -> None:
    batch = map_gallery_dl_extraction(
        extraction(), normalize_discovery_target("Reuters"), 2, NOW, "gallery-dl:test"
    )

    assert batch.profile.profile_id == "123"
    assert batch.asset_count == 2
    assert len(batch.posts) == 1
    assert batch.posts[0].assets[0].duration_ms == 12500
    assert batch.posts[0].assets[1].media_type is MediaType.ANIMATED_GIF
    assert batch.warnings == ("fixture warning",)
    assert batch.public_dict()["provider"] == "gallery-dl:test"


def test_maps_optional_fields_and_reply_type() -> None:
    data = extraction()
    last = GalleryDlExtraction(data.profile_record, (data.media_records[-1],))
    batch = map_gallery_dl_extraction(
        last, normalize_discovery_target("Reuters"), 1, NOW, "gallery-dl:test"
    )
    assert batch.posts[0].post_type is PostType.REPLY
    assert batch.posts[0].assets[0].width == 1280


def test_provider_uses_normalized_url_and_clock() -> None:
    calls: list[tuple[str, int]] = []

    def runner(url: str, limit: int) -> GalleryDlExtraction:
        calls.append((url, limit))
        return extraction()

    provider = GalleryDlDiscoveryProvider(runner, lambda: NOW)
    batch = provider.discover(normalize_discovery_target("@Reuters"), 1)
    assert calls == [("https://x.com/Reuters", 1)]
    assert batch.asset_count == 1
    assert batch.observed_at == NOW


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (RuntimeError("HTTP 429"), DiscoveryRateLimitError),
        (RuntimeError("profile locked; cookie required"), DiscoveryRestrictedError),
        (RuntimeError("network down"), DiscoveryError),
    ],
)
def test_classifies_external_errors(error: Exception, expected: type[Exception]) -> None:
    assert isinstance(_classified_error(error), expected)


def test_rejects_broken_or_cross_author_contract() -> None:
    data = extraction()
    broken = dict(data.media_records[0])
    broken.pop("tweet_id")
    with pytest.raises(DiscoveryContractError, match="required"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (broken,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )

    cross_author = dict(data.media_records[0])
    cross_author["author"] = {"id": 999, "name": "Other", "nick": "Other"}
    with pytest.raises(DiscoveryContractError, match="another author"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (cross_author,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


def test_empty_video_window_is_explicit() -> None:
    data = extraction()
    batch = map_gallery_dl_extraction(
        GalleryDlExtraction(data.profile_record, ()),
        normalize_discovery_target("Reuters"),
        2,
        NOW,
        "gallery-dl:test",
    )
    assert batch.asset_count == 0
    assert "No video assets" in batch.warnings[-1]


def test_limited_job_collects_only_video_and_stops_at_limit() -> None:
    data_job = _LimitedDataJob("https://x.com/Reuters", 2)
    data_job.handle_directory({"user": {"id": 123}})
    data_job.handle_url("image", {"type": "photo"})
    data_job.handle_url("video-1", {"type": "video"})
    with pytest.raises(exception.StopExtraction):
        data_job.handle_url("video-2", {"type": "animated_gif"})
    assert data_job.profile_record == {"user": {"id": 123}}
    assert [item["_source_url"] for item in data_job.media_records] == ["video-1", "video-2"]


def test_live_runner_boundary_has_no_download_and_classifies_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = extraction()

    class SuccessfulJob:
        exception: BaseException | None = None
        profile_record = data.profile_record
        media_records = list(data.media_records[:1])

        def __init__(self, url: str, limit: int) -> None:
            assert url == "https://x.com/Reuters/timeline"
            assert limit == 1

        def run(self) -> None:
            return None

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", SuccessfulJob)
    result = _run_gallery_dl("https://x.com/Reuters", 1)
    assert len(result.media_records) == 1
    assert config.get(("cache",), "file") == ":memory:"

    class FailedJob(SuccessfulJob):
        exception: BaseException | None = RuntimeError("HTTP 429")

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", FailedJob)
    with pytest.raises(DiscoveryRateLimitError):
        _run_gallery_dl("https://x.com/Reuters", 1)


def test_live_runner_rejects_missing_profile_and_constructor_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class EmptyJob:
        exception = None
        profile_record = None
        media_records: list[dict[str, object]] = []

        def __init__(self, url: str, limit: int) -> None:
            pass

        def run(self) -> None:
            return None

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", EmptyJob)
    with pytest.raises(DiscoveryContractError, match="profile metadata"):
        _run_gallery_dl("https://x.com/Reuters", 1)

    class BrokenJob(EmptyJob):
        def __init__(self, url: str, limit: int) -> None:
            raise RuntimeError("network down")

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", BrokenJob)
    with pytest.raises(DiscoveryError, match="discovery contract"):
        _run_gallery_dl("https://x.com/Reuters", 1)


def test_mapper_rejects_unsupported_media_and_nonnumeric_fields() -> None:
    data = extraction()
    unsupported = dict(data.media_records[0], type="photo")
    with pytest.raises(DiscoveryContractError, match="unsupported"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (unsupported,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )

    bad_width = dict(data.media_records[0], width={"bad": True})
    with pytest.raises(DiscoveryContractError, match="dimension"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (bad_width,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


@pytest.mark.parametrize(
    "message,kind",
    [
        ("404 NotFound sensitive", "DiscoveryNotFoundError"),
        ("connection timeout sensitive", "DiscoveryTransientError"),
        ("429 sensitive", "DiscoveryRateLimitError"),
        ("AuthRequired sensitive", "DiscoveryRestrictedError"),
        ("unknown sensitive", "DiscoveryContractError"),
    ],
)
def test_classification_does_not_expose_raw_response(message: str, kind: str) -> None:
    from xma.adapters.discovery.gallery_dl import _classified_error

    error = _classified_error(RuntimeError(message))
    assert type(error).__name__ == kind
    assert "sensitive" not in str(error)
