from datetime import UTC, datetime

import pytest

from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    normalize_discovery_target,
)
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import DomainError, InvalidIdentityError

NOW = datetime(2026, 10, 28, tzinfo=UTC)


@pytest.mark.parametrize(
    ("value", "handle"),
    [
        ("Reuters", "Reuters"),
        ("@Reuters", "Reuters"),
        ("https://x.com/Reuters", "Reuters"),
        ("https://twitter.com/Reuters", "Reuters"),
    ],
)
def test_normalize_public_profile_targets(value: str, handle: str) -> None:
    target = normalize_discovery_target(value)
    assert target.handle == handle
    assert target.canonical_url == "https://x.com/Reuters"


@pytest.mark.parametrize(
    "value",
    ["", "https://example.com/Reuters", "http://x.com/Reuters", "https://x.com/a/status/1"],
)
def test_rejects_non_profile_targets(value: str) -> None:
    with pytest.raises(InvalidIdentityError):
        normalize_discovery_target(value)


def test_batch_public_projection_omits_source_variants() -> None:
    target = normalize_discovery_target("@Reuters")
    profile = DiscoveredProfile("123", "Reuters", "Reuters")
    asset = DiscoveredAsset("9001", 0, MediaType.VIDEO, 1000, 100, 50, ("secret-url",))
    post = DiscoveredPost("9001", "123", "text", NOW, PostType.POST, (asset,))
    batch = DiscoveryBatch(target, "fixture:1", profile, (post,), NOW, 2)

    public = batch.public_dict()
    assert batch.asset_count == 1
    assert public["asset_count"] == 1
    assert "secret-url" not in str(public)


def test_batch_rejects_cross_profile_posts_and_limit_overflow() -> None:
    target = normalize_discovery_target("Reuters")
    profile = DiscoveredProfile("123", "Reuters", "Reuters")
    asset = DiscoveredAsset("9001", 0, MediaType.VIDEO, None, None, None, ("url",))
    other_post = DiscoveredPost("9001", "999", "", NOW, PostType.POST, (asset,))
    with pytest.raises(DomainError, match="target profile"):
        DiscoveryBatch(target, "fixture", profile, (other_post,), NOW, 1)

    post = DiscoveredPost("9001", "123", "", NOW, PostType.POST, (asset, asset))
    with pytest.raises(DomainError, match="exceeds"):
        DiscoveryBatch(target, "fixture", profile, (post,), NOW, 1)
