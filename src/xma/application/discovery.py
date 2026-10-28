"""Use cases for inspecting and synchronizing public profile metadata."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from xma.domain.discovery import DiscoveryBatch, normalize_discovery_target
from xma.domain.enums import RunStatus
from xma.domain.models import DiscoveryRun, MediaAsset, Post, Profile
from xma.domain.ports import DiscoveryProvider, UnitOfWork


@dataclass(frozen=True, slots=True)
class SyncResult:
    batch: DiscoveryBatch
    dry_run: bool
    run_id: str | None

    def public_dict(self) -> dict[str, object]:
        result = self.batch.public_dict()
        result.update({"dry_run": self.dry_run, "run_id": self.run_id})
        return result


class DiscoveryService:
    """Orchestrate provider discovery without leaking provider types."""

    def __init__(
        self,
        provider: DiscoveryProvider,
        unit_of_work_factory: Callable[[], UnitOfWork] | None = None,
        clock: Callable[[], datetime] | None = None,
        run_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._provider = provider
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock or (lambda: datetime.now(UTC))
        self._run_id_factory = run_id_factory or (lambda: str(uuid4()))

    def inspect(self, target: str, limit: int) -> DiscoveryBatch:
        normalized = normalize_discovery_target(target)
        return self._provider.discover(normalized, limit)

    def sync(self, target: str, limit: int, *, dry_run: bool = False) -> SyncResult:
        started_at = self._clock()
        batch = self.inspect(target, limit)
        if dry_run:
            return SyncResult(batch, True, None)
        if self._unit_of_work_factory is None:
            raise RuntimeError("sync requires a unit of work")

        finished_at = self._clock()
        run_id = self._run_id_factory()
        with self._unit_of_work_factory() as unit:
            catalog = unit.catalog
            current = catalog.get_profile(batch.profile.profile_id)
            created_at = batch.observed_at if current is None else current.created_at
            catalog.put_profile(
                Profile(
                    profile_id=batch.profile.profile_id,
                    handle=batch.profile.handle,
                    display_name=batch.profile.display_name,
                    observed_at=batch.observed_at,
                    created_at=created_at,
                    updated_at=batch.observed_at,
                )
            )
            for discovered_post in batch.posts:
                catalog.put_post(
                    Post(
                        post_id=discovered_post.post_id,
                        author_profile_id=discovered_post.author_profile_id,
                        canonical_url=f"https://x.com/i/status/{discovered_post.post_id}",
                        text=discovered_post.text,
                        published_at=discovered_post.published_at,
                        post_type=discovered_post.post_type,
                    )
                )
                for discovered_asset in discovered_post.assets:
                    catalog.put_media_asset(
                        MediaAsset(
                            post_id=discovered_asset.post_id,
                            media_index=discovered_asset.media_index,
                            media_type=discovered_asset.media_type,
                            duration_ms=discovered_asset.duration_ms,
                            width=discovered_asset.width,
                            height=discovered_asset.height,
                            variants=discovered_asset.variants,
                        )
                    )
            catalog.put_discovery_run(
                DiscoveryRun(
                    run_id=run_id,
                    strategy=batch.provider,
                    started_at=started_at,
                    status=RunStatus.COMPLETED,
                    finished_at=finished_at,
                    cursor=batch.cursor,
                    discovered_count=batch.asset_count,
                    error_count=0,
                )
            )
        return SyncResult(batch, False, run_id)
