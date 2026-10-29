"""Anonymous, no-download gallery-dl adapter for public X profiles."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from math import isfinite
from typing import Any, cast
from unicodedata import digit

import gallery_dl  # type: ignore[import-untyped]
from gallery_dl import config, exception, job

from xma.adapters.discovery.firefox_auth import (
    BrowserAuthentication,
    CookieFileAuthentication,
    load_cookie_file_x_cookies,
    load_firefox_x_cookies,
)
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
    DiscoveryNotFoundError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
    DiscoveryTransientError,
)

_VIDEO_TYPES = {"video", "animated_gif"}
_SQLITE_INTEGER_MAX = 2**63 - 1
_NUMERIC_CONTRACT_ERROR = "gallery-dl numeric metadata violates the B03 contract"


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


def _run_gallery_dl(
    url: str,
    limit: int,
    authentication: BrowserAuthentication | CookieFileAuthentication | None = None,
) -> GalleryDlExtraction:
    """Run gallery-dl as a library without loading user config or credentials."""
    config.clear()
    if authentication is None:
        cookie_source = None
    elif isinstance(authentication, BrowserAuthentication):
        cookie_source = load_firefox_x_cookies(authentication)
    else:
        cookie_source = load_cookie_file_x_cookies(authentication)
    config.set(("extractor",), "cookies", cookie_source)
    config.set(("extractor",), "cookies-update", False)
    config.set(("extractor",), "username", "")
    config.set(("extractor",), "password", "")
    config.set(("extractor", "twitter"), "cookies", cookie_source)
    config.set(("extractor", "twitter"), "cookies-update", False)
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
        return DiscoveryRateLimitError("provider request was limited [PROVIDER_RATE_LIMIT]")
    if (
        isinstance(error, TimeoutError)
        or "timeout" in detail
        or "timed out" in detail
        or "discoverydeadlineexceeded" in detail
    ):
        return DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
    if "502" in detail:
        return DiscoveryTransientError("temporary provider failure [PROVIDER_HTTP_502]")
    if "503" in detail:
        return DiscoveryTransientError("temporary provider failure [PROVIDER_HTTP_503]")
    if isinstance(error, ConnectionError) or any(
        word in detail for word in ("connection", "network down", "name resolution", "unreachable")
    ):
        return DiscoveryTransientError("temporary provider failure [PROVIDER_CONNECTION]")
    if any(word in detail for word in ("cookie", "login", "auth", "protected", "locked")):
        return DiscoveryRestrictedError("provider access is restricted [PROVIDER_RESTRICTED]")
    if any(word in detail for word in ("404", "notfound", "not found")):
        return DiscoveryNotFoundError("public profile was not found")
    return DiscoveryContractError("provider contract failure [PROVIDER_CONTRACT]")


class GalleryDlDiscoveryProvider:
    """Map gallery-dl metadata into provider-neutral discovery values."""

    def __init__(
        self,
        runner: GalleryDlRunner | None = None,
        clock: Callable[[], datetime] | None = None,
        authentication: BrowserAuthentication | CookieFileAuthentication | None = None,
    ) -> None:
        self._runner = runner or (lambda url, limit: _run_gallery_dl(url, limit, authentication))
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
        if target_user.get("protected") is not False:
            raise DiscoveryContractError("gallery-dl profile is not confirmed public")
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
            index = _source_index(_required(record, "num"))
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
    except (KeyError, TypeError, ValueError, OverflowError) as error:
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


def _bounded_integer(value: object, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
    try:
        if isinstance(value, float):
            if not isfinite(value) or not value.is_integer():
                raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
            result = int(value)
        else:
            result = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR) from error
    if result < minimum or result > maximum:
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
    return result


def _source_index(value: object) -> int:
    return _bounded_integer(value, minimum=1, maximum=_SQLITE_INTEGER_MAX + 1) - 1


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return _bounded_integer(value, minimum=0, maximum=_SQLITE_INTEGER_MAX)


def _has_negative_nonzero_significand(value: str) -> bool:
    normalized = value.strip()
    if not normalized.startswith("-"):
        return False
    significand = normalized[1:]
    exponent_index = next(
        (index for index, character in enumerate(significand) if character in "eE"),
        len(significand),
    )
    return any(digit(character, 0) != 0 for character in significand[:exponent_index])


def _duration_ms(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
    try:
        if isinstance(value, str):
            if _has_negative_nonzero_significand(value):
                raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
        elif isinstance(value, float) and (not isfinite(value) or value < 0):
            raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)

        seconds = float(value)
        milliseconds = seconds * 1000
        if not isfinite(seconds) or not isfinite(milliseconds):
            raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
        result = round(milliseconds)
    except (TypeError, ValueError, OverflowError) as error:
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR) from error
    if result < 0 or result > _SQLITE_INTEGER_MAX:
        raise DiscoveryContractError(_NUMERIC_CONTRACT_ERROR)
    return result


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
