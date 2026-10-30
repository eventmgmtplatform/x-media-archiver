"""B04 vertical-slice download orchestration."""

import hashlib
import json
import os
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from xma.application.discovery import DiscoveryService
from xma.domain.download import DownloadRequest, DownloadSummary
from xma.domain.enums import DownloadStatus, RunStatus
from xma.domain.errors import (
    DiscoveryError,
    DiscoveryTransientError,
    DownloadConflictError,
    DownloadError,
    ProviderExhaustedError,
)
from xma.domain.identity import media_identity
from xma.domain.models import Artifact, DiscoveryRun, DownloadJob, MediaAsset, Post, Profile
from xma.domain.ports import (
    DiscoveryProvider,
    IncrementalDiscoveryProvider,
    MediaDownloadProvider,
    UnitOfWork,
)


class DownloadService:
    """Discover, download, checksum, persist, and manifest at most ten assets."""

    def __init__(
        self,
        discovery_provider: DiscoveryProvider | None,
        media_provider: MediaDownloadProvider | None,
        unit_of_work_factory: Callable[[], UnitOfWork],
        repository: Path,
        *,
        clock: Callable[[], datetime] | None = None,
        run_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._discovery = (
            DiscoveryService(discovery_provider) if discovery_provider is not None else None
        )
        self._media = media_provider
        self._unit_of_work_factory = unit_of_work_factory
        self._repository = repository
        self._clock = clock or (lambda: datetime.now(UTC))
        self._run_id_factory = run_id_factory or (lambda: str(uuid4()))

    def execute(self, request: DownloadRequest) -> DownloadSummary:
        if self._discovery is None:
            raise DownloadError("discovery provider is unavailable")
        started_at = self._clock()
        batch = self._discovery.inspect(request.target, request.limit)
        run_id = self._run_id_factory()
        self._repository.mkdir(parents=True, exist_ok=True)
        self._persist_discovery(batch, run_id, started_at)

        downloaded = 0
        skipped = 0
        failed = 0
        manifest_artifacts: list[dict[str, object]] = []
        try:
            for post in batch.posts:
                for asset in post.assets:
                    result, was_skipped = self._download_asset(
                        batch.profile.handle,
                        batch.provider,
                        post,
                        asset,
                        run_id,
                    )
                    manifest_artifacts.append(result)
                    downloaded += not was_skipped
                    skipped += was_skipped
        except DownloadError:
            failed += 1
            self._write_manifest(
                request,
                run_id,
                started_at,
                self._clock(),
                manifest_artifacts,
                downloaded,
                skipped,
                failed,
            )
            raise

        finished_at = self._clock()
        self._write_manifest(
            request,
            run_id,
            started_at,
            finished_at,
            manifest_artifacts,
            downloaded,
            skipped,
            failed,
        )
        return DownloadSummary(
            batch.target.canonical_url,
            request.limit,
            downloaded,
            skipped,
            failed,
            run_id,
            tuple(manifest_artifacts),
            0,
            downloaded + skipped,
            True,
        )

    def execute_incremental(
        self,
        request: DownloadRequest,
        provider: IncrementalDiscoveryProvider | None,
        timeout_seconds: int,
        attempts: int,
        progress: Callable[[str], None],
        max_scan: int = 100,
    ) -> DownloadSummary:
        if attempts < 1 or attempts > 2:
            raise DownloadError("discovery attempts must be between 1 and 2")
        if not 1 <= max_scan <= 500:
            raise DownloadError("max scan must be between 1 and 500")
        from xma.domain.discovery import normalize_discovery_target

        normalized = normalize_discovery_target(request.target)
        manifest_request = DownloadRequest(
            normalized.canonical_url,
            request.limit,
            archive_all=request.archive_all,
        )
        identities, manifest_artifacts = self._load_existing(normalized.handle)
        existing_before = len(identities)
        run_id = self._run_id_factory()
        started_at = self._clock()
        downloaded = 0
        failed = 0
        attempted_failed: set[str] = set()
        if existing_before >= request.limit:
            self._write_manifest(
                manifest_request,
                run_id,
                started_at,
                self._clock(),
                manifest_artifacts,
                0,
                existing_before,
                0,
                existing_before=existing_before,
                complete=True,
            )
            return DownloadSummary(
                normalized.canonical_url,
                request.limit,
                0,
                existing_before,
                0,
                run_id,
                tuple(manifest_artifacts),
                existing_before,
                existing_before,
                True,
            )

        last_error: DiscoveryError | DownloadError | None = None
        provider_exhausted = False
        if provider is None:
            raise DownloadError("discovery provider is unavailable")
        for attempt in range(1, attempts + 1):
            progress(f"discovery attempt {attempt}/{attempts}")
            stream = provider.candidates(
                normalized,
                request.limit - len(identities),
                frozenset(identities | attempted_failed),
                timeout_seconds,
                max_scan,
            )
            try:
                for batch in stream:
                    for post in batch.posts:
                        for asset in post.assets:
                            identity = media_identity(asset.post_id, asset.media_index)
                            if identity in identities or identity in attempted_failed:
                                continue
                            self._repository.mkdir(parents=True, exist_ok=True)
                            candidate_run = self._run_id_factory()
                            self._persist_discovery(batch, candidate_run, self._clock())
                            try:
                                result, _ = self._download_asset(
                                    batch.profile.handle,
                                    batch.provider,
                                    post,
                                    asset,
                                    candidate_run,
                                )
                            except DownloadError as error:
                                last_error = error
                                attempted_failed.add(identity)
                                failed += 1
                                continue
                            identities.add(identity)
                            manifest_artifacts.append(result)
                            downloaded += 1
                            progress(f"downloaded {len(identities)}/{request.limit}")
                            self._write_manifest(
                                manifest_request,
                                run_id,
                                started_at,
                                self._clock(),
                                manifest_artifacts,
                                downloaded,
                                existing_before,
                                failed,
                                existing_before=existing_before,
                                complete=len(identities) >= request.limit,
                            )
                            if len(identities) >= request.limit:
                                break
                        if len(identities) >= request.limit:
                            break
                    if len(identities) >= request.limit:
                        break
            except ProviderExhaustedError as error:
                last_error = error
                provider_exhausted = True
            except DiscoveryError as error:
                last_error = error
            finally:
                close = getattr(stream, "close", None)
                if close is not None:
                    close()
            if len(identities) >= request.limit:
                break
            if provider_exhausted:
                break

        complete = len(identities) >= request.limit
        self._write_manifest(
            manifest_request,
            run_id,
            started_at,
            self._clock(),
            manifest_artifacts,
            downloaded,
            existing_before,
            failed,
            existing_before=existing_before,
            complete=complete,
            exhausted=not complete and not isinstance(last_error, DownloadError),
        )
        if not complete and not (request.archive_all and provider_exhausted):
            if last_error is not None:
                raise last_error
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_INCOMPLETE]")
        return DownloadSummary(
            normalized.canonical_url,
            request.limit,
            downloaded,
            existing_before,
            failed,
            run_id,
            tuple(manifest_artifacts),
            existing_before,
            len(identities),
            complete,
            provider_exhausted,
        )

    def verified_total(self, handle: str) -> int:
        """Return the target-scoped count after verifying catalog and filesystem state."""
        identities, _ = self._load_existing(handle)
        return len(identities)

    def _load_existing(self, handle: str) -> tuple[set[str], list[dict[str, object]]]:
        database = self._repository / "catalog.sqlite3"
        if not database.exists():
            if self._repository.exists() and any(
                path.name != ".archive.lock" for path in self._repository.iterdir()
            ):
                raise DownloadConflictError("catalog and filesystem do not agree")
            return set(), []
        identities: set[str] = set()
        manifest_artifacts: list[dict[str, object]] = []
        with self._unit_of_work_factory() as unit:
            jobs = {job.job_id: job for job in unit.catalog.list_download_jobs()}
            artifacts = unit.catalog.list_artifacts()
            artifact_jobs = {artifact.job_id for artifact in artifacts}
            completed_jobs = {
                job.job_id for job in jobs.values() if job.status is DownloadStatus.COMPLETED
            }
            if artifact_jobs != completed_jobs:
                raise DownloadConflictError("catalog and filesystem do not agree")
            for job in jobs.values():
                if job.status is DownloadStatus.FAILED_FINAL and job.job_id not in artifact_jobs:
                    post_id, media_index = job.asset_id.split(":", 1)
                    failed_directory = (
                        self._repository / "profiles" / handle / "posts" / post_id / media_index
                    )
                    if failed_directory.exists() and any(failed_directory.iterdir()):
                        raise DownloadConflictError("catalog and filesystem do not agree")
                elif job.status is not DownloadStatus.COMPLETED:
                    raise DownloadConflictError("catalog and filesystem do not agree")
            for artifact in artifacts:
                artifact_job = jobs.get(artifact.job_id)
                if artifact_job is None or artifact_job.status is not DownloadStatus.COMPLETED:
                    raise DownloadConflictError("catalog and filesystem do not agree")
                media = unit.catalog.get_media_asset(artifact_job.asset_id)
                if media is None:
                    raise DownloadConflictError("catalog and filesystem do not agree")
                absolute = self._repository / artifact.relative_path
                sidecar = absolute.parent / "metadata.json"
                if (
                    not absolute.is_file()
                    or absolute.stat().st_size != artifact.size_bytes
                    or _sha256(absolute) != artifact.sha256
                    or not sidecar.is_file()
                ):
                    raise DownloadConflictError("catalog and filesystem do not agree")
                try:
                    sidecar_data = json.loads(sidecar.read_text(encoding="utf-8"))
                except (OSError, ValueError) as error:
                    raise DownloadConflictError("catalog and filesystem do not agree") from error
                profile_handle = sidecar_data.get("profile_handle")
                if not isinstance(profile_handle, str):
                    raise DownloadConflictError("catalog and filesystem do not agree")
                if profile_handle.casefold() != handle.casefold():
                    continue
                identities.add(artifact_job.asset_id)
                manifest_artifacts.append(
                    _manifest_artifact(
                        artifact_job.asset_id,
                        artifact.relative_path,
                        artifact.size_bytes,
                        artifact.sha256,
                        sidecar.relative_to(self._repository).as_posix(),
                        str(sidecar_data.get("mime_type", artifact.mime_type)),
                        str(sidecar_data.get("extension", absolute.suffix)),
                        sidecar_data.get("width"),
                        sidecar_data.get("height"),
                    )
                )
        return identities, manifest_artifacts

    def _persist_discovery(self, batch: object, run_id: str, started_at: datetime) -> None:
        from xma.domain.discovery import DiscoveryBatch

        assert isinstance(batch, DiscoveryBatch)
        finished_at = self._clock()
        with self._unit_of_work_factory() as unit:
            catalog = unit.catalog
            current = catalog.get_profile(batch.profile.profile_id)
            created_at = batch.observed_at if current is None else current.created_at
            catalog.put_profile(
                Profile(
                    batch.profile.profile_id,
                    batch.profile.handle,
                    batch.profile.display_name,
                    batch.observed_at,
                    created_at,
                    batch.observed_at,
                )
            )
            for discovered_post in batch.posts:
                catalog.put_post(
                    Post(
                        discovered_post.post_id,
                        discovered_post.author_profile_id,
                        f"https://x.com/i/status/{discovered_post.post_id}",
                        discovered_post.text,
                        discovered_post.published_at,
                        discovered_post.post_type,
                    )
                )
                for discovered_asset in discovered_post.assets:
                    catalog.put_media_asset(
                        MediaAsset(
                            discovered_asset.post_id,
                            discovered_asset.media_index,
                            discovered_asset.media_type,
                            discovered_asset.duration_ms,
                            discovered_asset.width,
                            discovered_asset.height,
                            ("metadata-only",),
                        )
                    )
            catalog.put_discovery_run(
                DiscoveryRun(
                    run_id,
                    batch.provider,
                    started_at,
                    RunStatus.COMPLETED,
                    finished_at,
                    None,
                    batch.asset_count,
                    0,
                )
            )

    def _download_asset(
        self,
        handle: str,
        provider: str,
        post: object,
        asset: object,
        run_id: str,
    ) -> tuple[dict[str, object], bool]:
        from xma.domain.discovery import DiscoveredAsset, DiscoveredPost

        assert isinstance(post, DiscoveredPost)
        assert isinstance(asset, DiscoveredAsset)
        asset_id = media_identity(asset.post_id, asset.media_index)
        job_id = f"download:{asset.post_id}:{asset.media_index}"
        artifact_id = f"artifact:{asset.post_id}:{asset.media_index}"
        with self._unit_of_work_factory() as unit:
            existing_job = unit.catalog.get_download_job(job_id)
            existing_artifact = unit.catalog.get_artifact(artifact_id)

        if existing_job is not None or existing_artifact is not None:
            if (
                existing_job is not None
                and existing_job.status is DownloadStatus.FAILED_FINAL
                and existing_artifact is None
            ):
                job = existing_job.retry(self._clock())
            else:
                job = None
            if job is None and (
                existing_job is None
                or existing_artifact is None
                or existing_job.status is not DownloadStatus.COMPLETED
            ):
                raise DownloadConflictError("catalog and filesystem do not agree")
            if job is not None:
                pass
            else:
                assert existing_artifact is not None
                absolute = self._repository / existing_artifact.relative_path
                if (
                    not absolute.is_file()
                    or absolute.stat().st_size != existing_artifact.size_bytes
                    or _sha256(absolute) != existing_artifact.sha256
                ):
                    raise DownloadConflictError("catalog and filesystem do not agree")
                sidecar_relative = str(
                    Path(existing_artifact.relative_path).parent / "metadata.json"
                )
                sidecar_path = self._repository / sidecar_relative
                if not sidecar_path.is_file():
                    raise DownloadConflictError("catalog and filesystem do not agree")
                sidecar_data = json.loads(sidecar_path.read_text(encoding="utf-8"))
                return (
                    _manifest_artifact(
                        asset_id,
                        existing_artifact.relative_path,
                        existing_artifact.size_bytes,
                        existing_artifact.sha256,
                        sidecar_relative,
                        str(sidecar_data.get("mime_type", existing_artifact.mime_type)),
                        str(sidecar_data.get("extension", absolute.suffix)),
                        sidecar_data.get("width"),
                        sidecar_data.get("height"),
                    ),
                    True,
                )
        else:
            created_at = self._clock()
            job = DownloadJob(
                job_id,
                asset_id,
                run_id,
                DownloadStatus.DISCOVERED,
                0,
                created_at,
                created_at,
            )
            self._put_job(job)
            job = job.transition(DownloadStatus.QUEUED, self._clock())
        self._put_job(job)
        job = job.transition(DownloadStatus.DOWNLOADING, self._clock())
        self._put_job(job)

        directory = (
            self._repository
            / "profiles"
            / handle
            / "posts"
            / asset.post_id
            / str(asset.media_index)
        )
        part = directory / "video.part"
        sidecar = directory / "metadata.json"
        sidecar_tmp = directory / "metadata.json.tmp"
        final: Path | None = None
        directory.mkdir(parents=True, exist_ok=True)
        if part.exists() or sidecar.exists() or sidecar_tmp.exists():
            self._fail_job(job)
            raise DownloadConflictError("catalog and filesystem do not agree")
        try:
            if self._media is None:
                raise DownloadError("media download failed")
            downloaded = self._media.download(asset.variants[0], str(part))
            if (
                not part.is_file()
                or part.stat().st_size != downloaded.size_bytes
                or _sha256(part) != downloaded.sha256
            ):
                raise DownloadError("media download failed")
            final = directory / f"video{downloaded.extension}"
            if final.exists():
                raise DownloadConflictError("catalog and filesystem do not agree")
            relative_path = final.relative_to(self._repository).as_posix()
            sidecar_relative = sidecar.relative_to(self._repository).as_posix()
            downloaded_at = self._clock()
            sidecar_payload = {
                "schema_version": 1,
                "profile_handle": handle,
                "post_id": post.post_id,
                "media_index": asset.media_index,
                "asset_id": asset_id,
                "canonical_post_url": f"https://x.com/i/status/{post.post_id}",
                "published_at": post.published_at.isoformat(),
                "post_type": post.post_type.value,
                "text": post.text,
                "media_type": asset.media_type.value,
                "duration_ms": asset.duration_ms,
                "width": asset.width,
                "height": asset.height,
                "provider": provider,
                "downloaded_at": downloaded_at.isoformat(),
                "relative_path": relative_path,
                "mime_type": downloaded.mime_type,
                "extension": downloaded.extension,
                "quality_policy": "provider-best",
                "size_bytes": downloaded.size_bytes,
                "sha256": downloaded.sha256,
            }
            sidecar_tmp.write_text(
                json.dumps(sidecar_payload, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(part, final)
            os.replace(sidecar_tmp, sidecar)
            completed = job.transition(DownloadStatus.COMPLETED, downloaded_at)
            artifact = Artifact(
                artifact_id,
                job_id,
                relative_path,
                downloaded.mime_type,
                downloaded.size_bytes,
                downloaded.sha256,
                downloaded_at,
            )
            with self._unit_of_work_factory() as unit:
                unit.catalog.put_download_job(completed)
                unit.catalog.put_artifact(artifact)
            return (
                _manifest_artifact(
                    asset_id,
                    relative_path,
                    downloaded.size_bytes,
                    downloaded.sha256,
                    sidecar_relative,
                    downloaded.mime_type,
                    downloaded.extension,
                    asset.width,
                    asset.height,
                ),
                False,
            )
        except DownloadError as error:
            self._cleanup(directory, part, sidecar_tmp, sidecar, final)
            self._fail_job(job, str(error))
            raise
        except (OSError, ValueError) as error:
            self._cleanup(directory, part, sidecar_tmp, sidecar, final)
            self._fail_job(job, "MEDIA_DOWNLOAD_FAILED")
            raise DownloadError("media download failed") from error

    def _put_job(self, job: DownloadJob) -> None:
        with self._unit_of_work_factory() as unit:
            unit.catalog.put_download_job(job)

    def _fail_job(self, job: DownloadJob, code: str = "MEDIA_DOWNLOAD_FAILED") -> None:
        allowed = {
            "MEDIA_URL_EXPIRED",
            "MEDIA_FORBIDDEN",
            "MEDIA_NOT_FOUND",
            "MEDIA_RATE_LIMITED",
            "MEDIA_TIMEOUT",
            "MEDIA_SERVER_ERROR",
            "MEDIA_CONNECTION_FAILED",
            "MEDIA_CONTENT_INVALID",
            "MEDIA_DOWNLOAD_FAILED",
        }
        sanitized = code if code in allowed else "MEDIA_DOWNLOAD_FAILED"
        failed = job.transition(
            DownloadStatus.FAILED_FINAL,
            self._clock(),
            error_code=sanitized,
            error_message="media download failed",
        )
        self._put_job(failed)

    @staticmethod
    def _cleanup(directory: Path, *paths: Path | None) -> None:
        for path in paths:
            if path is not None:
                path.unlink(missing_ok=True)
        with suppress(OSError):
            directory.rmdir()

    def _write_manifest(
        self,
        request: DownloadRequest,
        run_id: str,
        started_at: datetime,
        finished_at: datetime,
        artifacts: list[dict[str, object]],
        downloaded: int,
        skipped: int,
        failed: int,
        *,
        existing_before: int = 0,
        complete: bool = True,
        exhausted: bool = False,
    ) -> None:
        directory = self._repository / "manifests"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / "latest.json"
        temporary = directory / "latest.json.tmp"
        payload = {
            "schema_version": 1,
            "target": request.target,
            "requested_limit": request.limit,
            "downloaded_count": downloaded,
            "skipped_count": skipped,
            "failed_count": failed,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "run_id": run_id,
            "artifacts": artifacts,
            "requested_total": request.limit,
            "existing_before": existing_before,
            "downloaded_this_run": downloaded,
            "total_after": existing_before + downloaded,
            "complete": complete,
            "exhausted": exhausted,
            "quality_policy": "provider-best",
        }
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, destination)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_artifact(
    asset_id: str,
    relative_path: str,
    size_bytes: int,
    sha256: str,
    sidecar_path: str,
    mime_type: str,
    extension: str,
    width: object,
    height: object,
) -> dict[str, object]:
    return {
        "asset_id": asset_id,
        "relative_path": relative_path,
        "size_bytes": size_bytes,
        "sha256": sha256,
        "sidecar_path": sidecar_path,
        "mime_type": mime_type,
        "extension": extension,
        "width": width,
        "height": height,
        "quality_policy": "provider-best",
    }
