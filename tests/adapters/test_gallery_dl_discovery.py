import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from gallery_dl import config, exception  # type: ignore[import-untyped]

from xma.adapters.discovery.firefox_auth import BrowserAuthentication
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
SENSITIVE_MARKER = "SYNTHETIC-SIGNED-URL-SECRET"
NUMERIC_ERROR = "gallery-dl numeric metadata violates the B03 contract"


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


def test_live_runner_configures_firefox_session_without_export(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = extraction()

    class SuccessfulJob:
        exception: BaseException | None = None
        profile_record = data.profile_record
        media_records = list(data.media_records[:1])

        def __init__(self, url: str, limit: int) -> None:
            pass

        def run(self) -> None:
            return None

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", SuccessfulJob)
    authentication = BrowserAuthentication("firefox", "synthetic-profile")
    monkeypatch.setattr(
        "xma.adapters.discovery.gallery_dl.load_firefox_x_cookies",
        lambda value: {
            "auth_token": "synthetic-auth-value",
            "ct0": "synthetic-csrf-value",
        },
    )

    _run_gallery_dl("https://x.com/Reuters", 1, authentication)

    expected = {
        "auth_token": "synthetic-auth-value",
        "ct0": "synthetic-csrf-value",
    }
    assert config.get(("extractor", "twitter"), "cookies") == expected
    assert config.get(("extractor", "twitter"), "cookies-update") is False
    assert config.get(("cache",), "file") == ":memory:"
    assert config.get(("extractor",), "download") is False
    assert config.get(("downloader",), "enabled") is False


@pytest.mark.parametrize(
    ("browser", "profile"),
    [
        ("chromium", "profile"),
        ("firefox", ""),
        ("firefox", "."),
        ("firefox", ".."),
        ("firefox", "../profile"),
        ("firefox", "a" * 129),
    ],
)
def test_browser_authentication_rejects_unsupported_or_path_values(
    browser: str, profile: str
) -> None:
    with pytest.raises(ValueError, match="browser authentication configuration is invalid"):
        BrowserAuthentication(browser, profile)


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


def test_authenticated_reader_failure_does_not_continue_anonymously(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = "SYNTHETIC-READER-ERROR-MARKER"

    def fail(authentication: BrowserAuthentication) -> dict[str, str]:
        raise DiscoveryRestrictedError("authenticated Firefox session is unavailable")

    class UnexpectedJob:
        def __init__(self, url: str, limit: int) -> None:
            raise AssertionError("authenticated failure must not construct an anonymous job")

    monkeypatch.setattr("xma.adapters.discovery.gallery_dl.load_firefox_x_cookies", fail)
    monkeypatch.setattr("xma.adapters.discovery.gallery_dl._LimitedDataJob", UnexpectedJob)

    with pytest.raises(DiscoveryRestrictedError) as captured:
        _run_gallery_dl(
            "https://x.com/Reuters",
            1,
            BrowserAuthentication("firefox", "synthetic-profile"),
        )

    assert str(captured.value) == "authenticated Firefox session is unavailable"
    assert marker not in str(captured.value)


@pytest.mark.parametrize("protected", [True, None, "false", 0, object()])
def test_mapper_rejects_profile_not_explicitly_public(protected: object) -> None:
    data = extraction()
    profile_record = dict(data.profile_record)
    profile_record["user"] = dict(profile_record["user"], protected=protected)

    with pytest.raises(DiscoveryContractError, match="profile is not confirmed public"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(profile_record, data.media_records),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


def test_mapper_rejects_missing_profile_protection_state() -> None:
    data = extraction()
    profile_record = dict(data.profile_record)
    user = dict(profile_record["user"])
    user.pop("protected")
    profile_record["user"] = user

    with pytest.raises(DiscoveryContractError, match="profile is not confirmed public"):
        map_gallery_dl_extraction(
            GalleryDlExtraction(profile_record, data.media_records),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


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
    with pytest.raises(DiscoveryContractError, match=NUMERIC_ERROR):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (bad_width,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


@pytest.mark.parametrize("field", ["num", "width", "height", "duration"])
@pytest.mark.parametrize(
    "invalid",
    [float("nan"), float("inf"), float("-inf"), True, False, json.loads("1e400")],
    ids=["nan", "positive-infinity", "negative-infinity", "true", "false", "json-1e400"],
)
def test_mapper_rejects_invalid_numeric_metadata(field: str, invalid: object) -> None:
    data = extraction()
    record = dict(data.media_records[0], **{field: invalid})
    record["_source_url"] = f"https://media.invalid/video?signature={SENSITIVE_MARKER}"

    with pytest.raises(DiscoveryContractError) as captured:
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (record,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )

    assert str(captured.value) == NUMERIC_ERROR
    assert SENSITIVE_MARKER not in str(captured.value)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("num", 0),
        ("num", -1),
        ("num", 1.5),
        ("num", 2**63 + 1),
        ("width", -1),
        ("height", 2**63),
        ("duration", -0.001),
        ("duration", 1e308),
    ],
)
def test_mapper_rejects_out_of_range_or_fractional_metadata(field: str, invalid: object) -> None:
    data = extraction()
    record = dict(data.media_records[0], **{field: invalid})
    with pytest.raises(DiscoveryContractError, match=NUMERIC_ERROR):
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (record,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )


@pytest.mark.parametrize(
    "invalid",
    [-0.0001, -0.0005, -5e-324, "-0.0001", "-1e-400"],
    ids=["tenth-ms", "half-ms", "negative-subnormal", "string-tenth-ms", "string-extreme"],
)
def test_mapper_rejects_every_semantically_negative_duration(invalid: object) -> None:
    data = extraction()
    record = dict(data.media_records[0], duration=invalid)

    with pytest.raises(DiscoveryContractError) as captured:
        map_gallery_dl_extraction(
            GalleryDlExtraction(data.profile_record, (record,)),
            normalize_discovery_target("Reuters"),
            1,
            NOW,
            "gallery-dl:test",
        )

    assert str(captured.value) == NUMERIC_ERROR


@pytest.mark.parametrize(
    ("duration", "expected_ms"),
    [
        (0, 0),
        (0.0001, 0),
        (0.0005, 0),
        (0.0015, 2),
        (0.0025, 2),
        (0.0045, 4),
        ("0.0005", 0),
        ("0.0025", 2),
        ("1e-400", 0),
        ("12.5", 12500),
    ],
    ids=[
        "zero",
        "positive-under-half-ms",
        "float-half-ms",
        "float-one-and-half-ms",
        "float-two-and-half-ms",
        "float-four-and-half-ms",
        "string-half-ms",
        "string-two-and-half-ms",
        "positive-extreme",
        "existing",
    ],
)
def test_mapper_preserves_nonnegative_duration_rounding(duration: object, expected_ms: int) -> None:
    data = extraction()
    record = dict(data.media_records[0], duration=duration)
    batch = map_gallery_dl_extraction(
        GalleryDlExtraction(data.profile_record, (record,)),
        normalize_discovery_target("Reuters"),
        1,
        NOW,
        "gallery-dl:test",
    )

    assert batch.posts[0].assets[0].duration_ms == expected_ms


@pytest.mark.parametrize(
    ("duration", "expected_ms"),
    [
        ("1e-1999999999999999998", 0),
        ("0e1000000000000000000", 0),
        ("-1e-1999999999999999998", None),
        ("-0e1000000000000000000", 0),
    ],
    ids=["positive-underflow", "positive-zero", "negative-underflow", "negative-zero"],
)
def test_mapper_preserves_extreme_exponent_compatibility(
    duration: str, expected_ms: int | None
) -> None:
    data = extraction()
    record = dict(data.media_records[0], duration=duration)
    if expected_ms is None:
        with pytest.raises(DiscoveryContractError, match=NUMERIC_ERROR):
            map_gallery_dl_extraction(
                GalleryDlExtraction(data.profile_record, (record,)),
                normalize_discovery_target("Reuters"),
                1,
                NOW,
                "gallery-dl:test",
            )
        return

    batch = map_gallery_dl_extraction(
        GalleryDlExtraction(data.profile_record, (record,)),
        normalize_discovery_target("Reuters"),
        1,
        NOW,
        "gallery-dl:test",
    )
    assert batch.posts[0].assets[0].duration_ms == expected_ms


def test_mapper_preserves_finite_numeric_values() -> None:
    data = extraction()
    record = dict(
        data.media_records[0],
        num="1",
        width=1920.0,
        height="1080",
        duration="12.5",
    )
    batch = map_gallery_dl_extraction(
        GalleryDlExtraction(data.profile_record, (record,)),
        normalize_discovery_target("Reuters"),
        1,
        NOW,
        "gallery-dl:test",
    )
    asset = batch.posts[0].assets[0]
    assert (asset.media_index, asset.width, asset.height, asset.duration_ms) == (
        0,
        1920,
        1080,
        12500,
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
