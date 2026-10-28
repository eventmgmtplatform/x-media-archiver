"""Anonymous, no-download gallery-dl adapter for public X profiles."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast

import gallery_dl  # type: ignore[import-untyped]
from gallery_dl import config, exception, job

from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import (
    DiscoveryContractError,
    DiscoveryError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
)

_VIDEO_TYPES = {"video", "animated_gif"}


@dataclass(frozen=True, slots=True)
class GalleryDlExtraction:
    profile_record: Mapping[str, Any]
    media_records: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...] = ()


GalleryDlRunner = Callable[[str, int], GalleryDlExtraction]


class _LimitedDataJob(job.DataJob):  # type: ignore[misc]
    """Collect only video metadata and stop extraction at the requested limit."""

    def __init__(self, url: str, limit: int) -> None:
        super().__init__(url, file=None)
        self.limit = limit
        self.profile_record: dict[str, Any] | None = None
        self.media_records: list[dict[str, Any]] = []

    def handle_directory(self, kwdict: Mapping[str, Any]) -> None:
        if self.profile_record is None:
            self.profile_record = dict(kwdict)

    def handle_url(self, url: str, kwdict: Mapping[str, Any]) -> None:
        if str(kwdict.get("type", "")).lower() not in _VIDEO_TYPES:
            return
        record = dict(kwdict)
        record["_source_url"] = url
        self.media_records.append(record)
        if len(self.media_records) >= self.limit:
            raise exception.StopExtraction


def _run_gallery_dl(url: str, limit: int) -> GalleryDlExtraction:
    """Run gallery-dl as a library without loading user config or credentials."""
    config.clear()
    config.set(("extractor",), "cookies", None)
    config.set(("extractor",), "username", "")
    config.set(("extractor",), "password", "")
    config.set(("extractor", "twitter"), "cookies", None)
    config.set(("extractor", "twitter"), "username", "")
    config.set(("extractor", "twitter"), "password", "")
    config.set(("extractor", "twitter"), "include", ["timeline"])
    config.set(("extractor", "twitter"), "videos", True)
    config.set(("extractor", "twitter"), "previews", False)
    config.set(("extractor", "twitter"), "retweets", False)
    config.set(("extractor", "twitter"), "quoted", False)
    config.set(("extractor", "twitter"), "text-tweets", False)
    config.set(("extractor",), "download", False)
    config.set(("downloader",), "enabled", False)
    # Keep discovery read-only with respect to the host filesystem. gallery-dl
    # otherwise creates ~/.cache/gallery-dl/cache.sqlite3 for guest tokens.
    config.set(("cache",), "file", ":memory:")
    config.set(("output",), "private", False)

    try:
        # Target the concrete child extractor. DataJob intentionally does not
        # follow queue messages unless recursive resolution is requested.
        data_job = _LimitedDataJob(url.rstrip("/") + "/timeline", limit)
        data_job.run()
    except Exception as error:
        raise _classified_error(error) from error
    if data_job.exception is not None:
        raise _classified_error(data_job.exception)
    profile_record = data_job.profile_record
    if profile_record is None and data_job.media_records:
        profile_record = data_job.media_records[0]
    if profile_record is None:
        raise DiscoveryContractError("gallery-dl returned no public profile metadata")
    return GalleryDlExtraction(profile_record, tuple(data_job.media_records))


def _classified_error(error: BaseException) -> DiscoveryError:
    detail = f"{error.__class__.__name__}: {error}".lower()
    if "429" in detail or "rate limit" in detail or "ratelimit" in detail:
        return DiscoveryRateLimitError("gallery-dl was rate limited")
    if any(word in detail for word in ("cookie", "login", "auth", "protected", "locked")):
        return DiscoveryRestrictedError("profile is not available anonymously")
    return DiscoveryError(f"gallery-dl discovery failed ({error.__class__.__name__})")


class GalleryDlDiscoveryProvider:
    """Map gallery-dl metadata into provider-neutral discovery values."""

    def __init__(
        self,
        runner: GalleryDlRunner | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._runner = runner or _run_gallery_dl
        self._clock = clock or (lambda: datetime.now(UTC))

    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        if limit < 1 or limit > 100:
            raise DiscoveryContractError("limit must be between 1 and 100")
        extraction = self._runner(target.canonical_url, limit)
        return map_gallery_dl_extraction(
            extraction,
            target,
            limit,
            self._clock(),
            f"gallery-dl:{gallery_dl.__version__}",
        )


def map_gallery_dl_extraction(
    extraction: GalleryDlExtraction,
    target: DiscoveryTarget,
    limit: int,
    observed_at: datetime,
    provider: str,
) -> DiscoveryBatch:
    """Pure contract mapper used by offline fixtures and the live adapter."""
    try:
        target_user = _mapping(extraction.profile_record.get("user"), "user")
        profile = DiscoveredProfile(
            str(_required(target_user, "id")),
            str(_required(target_user, "name")),
            str(target_user.get("nick") or _required(target_user, "name")),
        )
        grouped: dict[str, tuple[dict[str, Any], list[DiscoveredAsset]]] = {}
        seen_assets: set[tuple[str, int]] = set()
        for record in extraction.media_records[:limit]:
            media_type = _media_type(record.get("type"))
            post_id = str(_required(record, "tweet_id"))
            author = _mapping(record.get("author"), "author")
            author_id = str(_required(author, "id"))
            if author_id != profile.profile_id:
                raise DiscoveryContractError("gallery-dl returned media from another author")
            index = int(_required(record, "num")) - 1
            key = (post_id, index)
            if key in seen_assets:
                continue
            seen_assets.add(key)
            source_url = str(_required(record, "_source_url"))
            asset = DiscoveredAsset(
                post_id=post_id,
                media_index=index,
                media_type=media_type,
                duration_ms=_duration_ms(record.get("duration")),
                width=_optional_int(record.get("width")),
                height=_optional_int(record.get("height")),
                variants=(source_url,),
            )
            metadata, assets = grouped.setdefault(post_id, (dict(record), []))
            if str(_required(_mapping(metadata.get("author"), "author"), "id")) != author_id:
                raise DiscoveryContractError("inconsistent author metadata for one post")
            assets.append(asset)

        posts = tuple(
            DiscoveredPost(
                post_id=post_id,
                author_profile_id=profile.profile_id,
                text=str(metadata.get("content") or ""),
                published_at=_datetime(metadata.get("date")),
                post_type=_post_type(metadata),
                assets=tuple(sorted(assets, key=lambda asset: asset.media_index)),
            )
            for post_id, (metadata, assets) in grouped.items()
        )
    except DiscoveryContractError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise DiscoveryContractError(
            "gallery-dl output does not satisfy the B03 contract"
        ) from error

    warnings = tuple(extraction.warnings)
    if not posts:
        warnings += ("No video assets were observed within the public extraction window.",)
    return DiscoveryBatch(
        target=target,
        provider=provider,
        profile=profile,
        posts=posts,
        observed_at=observed_at,
        requested_limit=limit,
        cursor=None,
        warnings=warnings,
    )


def _required(value: Mapping[str, Any], key: str) -> Any:
    result = value.get(key)
    if result is None or result == "":
        raise DiscoveryContractError(f"gallery-dl field {key!r} is required")
    return result


def _mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DiscoveryContractError(f"gallery-dl field {field!r} must be an object")
    return cast(Mapping[str, Any], value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise DiscoveryContractError("gallery-dl dimension must be numeric")
    return int(value)


def _duration_ms(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise DiscoveryContractError("gallery-dl duration must be numeric")
    return round(float(value) * 1000)


def _datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise DiscoveryContractError("gallery-dl field 'date' must be a timestamp")
    return result.replace(tzinfo=UTC) if result.tzinfo is None else result.astimezone(UTC)


def _media_type(value: object) -> MediaType:
    return {
        "video": MediaType.VIDEO,
        "animated_gif": MediaType.ANIMATED_GIF,
    }.get(str(value).lower()) or _unsupported_media_type(value)


def _unsupported_media_type(value: object) -> MediaType:
    raise DiscoveryContractError(f"unsupported gallery-dl media type: {value!r}")


def _post_type(metadata: Mapping[str, Any]) -> PostType:
    if metadata.get("retweet_id"):
        return PostType.REPOST
    if metadata.get("quoted_id"):
        return PostType.QUOTE
    if metadata.get("reply_id"):
        return PostType.REPLY
    return PostType.POST
