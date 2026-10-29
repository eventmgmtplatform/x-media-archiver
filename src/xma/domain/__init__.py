"""Domain entities and contracts for the X media catalog."""

from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
    DiscoveryTargetKind,
    normalize_discovery_target,
)
from xma.domain.enums import DownloadStatus, MediaType, PostType, RunStatus
from xma.domain.models import Artifact, DiscoveryRun, DownloadJob, MediaAsset, Post, Profile

__all__ = [
    "Artifact",
    "DiscoveredAsset",
    "DiscoveredPost",
    "DiscoveredProfile",
    "DiscoveryBatch",
    "DiscoveryRun",
    "DiscoveryTarget",
    "DiscoveryTargetKind",
    "DownloadJob",
    "DownloadStatus",
    "MediaAsset",
    "MediaType",
    "Post",
    "PostType",
    "Profile",
    "RunStatus",
    "normalize_discovery_target",
]
