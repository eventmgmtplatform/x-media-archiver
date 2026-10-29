"""Provider-neutral discovery values used by application services."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from urllib.parse import urlparse

from xma.domain.enums import MediaType, PostType
from xma.domain.errors import DomainError, InvalidIdentityError
from xma.domain.identity import normalize_handle, utc_datetime, validate_non_negative, validate_x_id


class DiscoveryTargetKind(StrEnum):
    """Explicit provider traversal mode."""

    PROFILE = "PROFILE"
    SINGLE_POST = "SINGLE_POST"


@dataclass(frozen=True, slots=True)
class DiscoveryTarget:
    """Normalized public X profile or single-post target."""

    handle: str
    kind: DiscoveryTargetKind = DiscoveryTargetKind.PROFILE
    post_id: str | None = None

    def __post_init__(self) -> None:
        if self.kind is DiscoveryTargetKind.SINGLE_POST:
            if self.post_id is None:
                raise InvalidIdentityError("single-post target requires a post ID")
            validate_x_id(self.post_id, "post_id")
        elif self.post_id is not None:
            raise InvalidIdentityError("profile target must not include a post ID")

    @property
    def canonical_url(self) -> str:
        base = f"https://x.com/{self.handle}"
        if self.kind is DiscoveryTargetKind.SINGLE_POST:
            return f"{base}/status/{self.post_id}"
        return base


def normalize_discovery_target(value: str) -> DiscoveryTarget:
    """Accept a handle or a public X/Twitter profile URL."""
    raw = value.strip()
    if not raw:
        raise InvalidIdentityError("target must not be blank")
    if "://" not in raw:
        return DiscoveryTarget(normalize_handle(raw))

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    profile_hosts = {
        "x.com",
        "www.x.com",
        "mobile.x.com",
        "twitter.com",
        "www.twitter.com",
        "mobile.twitter.com",
    }
    if parsed.scheme != "https" or host not in profile_hosts:
        raise InvalidIdentityError("target URL must be an HTTPS X or Twitter profile")
    parts = tuple(part for part in parsed.path.split("/") if part)
    status_hosts = {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}
    if len(parts) == 3 and parts[1] == "status":
        if host not in status_hosts or not parts[2].isdecimal():
            raise InvalidIdentityError("target URL must identify one public X status")
        return DiscoveryTarget(
            normalize_handle(parts[0]),
            DiscoveryTargetKind.SINGLE_POST,
            validate_x_id(parts[2], "post_id"),
        )
    if len(parts) != 1 or parsed.query or parsed.fragment:
        raise InvalidIdentityError("target URL must identify one public profile")
    return DiscoveryTarget(normalize_handle(parts[0]))


@dataclass(frozen=True, slots=True)
class DiscoveredProfile:
    profile_id: str
    handle: str
    display_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", validate_x_id(self.profile_id, "profile_id"))
        object.__setattr__(self, "handle", normalize_handle(self.handle))
        if not self.display_name.strip():
            raise DomainError("display_name must not be blank")


@dataclass(frozen=True, slots=True)
class DiscoveredAsset:
    post_id: str
    media_index: int
    media_type: MediaType
    duration_ms: int | None
    width: int | None
    height: int | None
    variants: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_x_id(self.post_id, "post_id")
        validate_non_negative(self.media_index, "media_index")
        for field in ("duration_ms", "width", "height"):
            value = getattr(self, field)
            if value is not None:
                validate_non_negative(value, field)
        if not self.variants or any(not value.strip() for value in self.variants):
            raise DomainError("discovered asset must contain non-blank variants")


@dataclass(frozen=True, slots=True)
class DiscoveredPost:
    post_id: str
    author_profile_id: str
    text: str
    published_at: datetime
    post_type: PostType
    assets: tuple[DiscoveredAsset, ...]

    def __post_init__(self) -> None:
        validate_x_id(self.post_id, "post_id")
        validate_x_id(self.author_profile_id, "author_profile_id")
        object.__setattr__(self, "published_at", utc_datetime(self.published_at, "published_at"))
        if not self.assets or any(asset.post_id != self.post_id for asset in self.assets):
            raise DomainError("discovered post must contain assets belonging to the post")


@dataclass(frozen=True, slots=True)
class DiscoveryBatch:
    target: DiscoveryTarget
    provider: str
    profile: DiscoveredProfile
    posts: tuple[DiscoveredPost, ...]
    observed_at: datetime
    requested_limit: int
    cursor: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise DomainError("provider must not be blank")
        object.__setattr__(self, "observed_at", utc_datetime(self.observed_at, "observed_at"))
        if self.requested_limit < 1 or self.requested_limit > 100:
            raise DomainError("requested_limit must be between 1 and 100")
        if self.asset_count > self.requested_limit:
            raise DomainError("discovery result exceeds requested_limit")
        if any(post.author_profile_id != self.profile.profile_id for post in self.posts):
            raise DomainError("all discovered posts must belong to the target profile")

    @property
    def asset_count(self) -> int:
        return sum(len(post.assets) for post in self.posts)

    def public_dict(self) -> dict[str, object]:
        """Return stable output without signed media URLs."""
        return {
            "target": self.target.canonical_url,
            "provider": self.provider,
            "profile": {
                "id": self.profile.profile_id,
                "handle": self.profile.handle,
                "display_name": self.profile.display_name,
            },
            "observed_at": self.observed_at.isoformat(),
            "requested_limit": self.requested_limit,
            "post_count": len(self.posts),
            "asset_count": self.asset_count,
            "cursor": self.cursor,
            "warnings": list(self.warnings),
            "posts": [
                {
                    "id": post.post_id,
                    "url": f"https://x.com/i/status/{post.post_id}",
                    "text": post.text,
                    "published_at": post.published_at.isoformat(),
                    "type": post.post_type.value,
                    "assets": [
                        {
                            "index": asset.media_index,
                            "type": asset.media_type.value,
                            "duration_ms": asset.duration_ms,
                            "width": asset.width,
                            "height": asset.height,
                            "variant_count": len(asset.variants),
                        }
                        for asset in post.assets
                    ],
                }
                for post in self.posts
            ],
        }
