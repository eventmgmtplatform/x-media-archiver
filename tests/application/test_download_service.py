"""Offline tests for the B04 download vertical slice."""

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.application.download import DownloadService
from xma.domain.discovery import (
    DiscoveredAsset,
    DiscoveredPost,
    DiscoveredProfile,
    DiscoveryBatch,
    DiscoveryTarget,
)
from xma.domain.download import DownloadedArtifact, DownloadRequest
from xma.domain.enums import MediaType, PostType
from xma.domain.errors import (
    DiscoveryTransientError,
    DomainError,
    DownloadConflictError,
    DownloadError,
)

NOW = datetime(2026, 10, 28, 12, tzinfo=UTC)


class FixtureDiscovery:
    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        posts = tuple(
            DiscoveredPost(
                str(9000 + index),
                "123",
                f"post {index}",
                NOW,
                PostType.POST,
                (
                    DiscoveredAsset(
                        str(9000 + index),
                        0,
                        MediaType.VIDEO,
                        1000,
                        1280,
                        720,
                        (f"https://media.invalid/video-{index}.mp4?signature=private",),
                    ),
                ),
            )
            for index in range(limit)
        )
        return DiscoveryBatch(
            target,
            "fixture:download",
            DiscoveredProfile("123", target.handle, "Reuters"),
            posts,
            NOW,
            limit,
        )


class FixtureMedia:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.part_observed = False

    def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
        assert "signature=private" in source_url
        path = Path(part_path)
        assert path.suffix == ".part"
        payload = f"synthetic-video:{source_url.rsplit('/', 1)[-1].split('?', 1)[0]}".encode()
        path.write_bytes(payload)
        self.part_observed = path.is_file()
        if self.fail:
            raise DownloadError("media download failed")
        return DownloadedArtifact(
            "video/mp4",
            len(payload),
            hashlib.sha256(payload).hexdigest(),
            ".mp4",
        )


def _service(repository: Path, media: FixtureMedia) -> DownloadService:
    database = repository / "catalog.sqlite3"
    return DownloadService(
        FixtureDiscovery(),
        media,
        lambda: SQLiteUnitOfWork(database),
        repository,
        clock=lambda: NOW,
        run_id_factory=lambda: "download-run",
    )


def _candidate_batch(target: DiscoveryTarget, index: int) -> DiscoveryBatch:
    post_id = str(9000 + index)
    return DiscoveryBatch(
        target,
        "fixture:incremental",
        DiscoveredProfile("123", target.handle, "Reuters"),
        (
            DiscoveredPost(
                post_id,
                "123",
                f"post {index}",
                NOW,
                PostType.POST,
                (
                    DiscoveredAsset(
                        post_id,
                        0,
                        MediaType.VIDEO,
                        1000,
                        1280,
                        720,
                        (f"https://media.invalid/video-{index}.mp4?signature=private",),
                    ),
                ),
            ),
        ),
        NOW,
        1,
    )


class IncrementalFixture:
    def __init__(self, indices_by_attempt: list[list[int]], *, timeout: bool = False) -> None:
        self.indices_by_attempt = indices_by_attempt
        self.timeout = timeout
        self.calls: list[tuple[int, frozenset[str], int]] = []

    def candidates(
        self,
        target: DiscoveryTarget,
        remaining: int,
        existing_identities: frozenset[str],
        timeout_seconds: int,
    ) -> Iterator[DiscoveryBatch]:
        call = len(self.calls)
        self.calls.append((remaining, existing_identities, timeout_seconds))
        for index in self.indices_by_attempt[call]:
            yield _candidate_batch(target, index)
        if self.timeout:
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")


def _incremental_service(repository: Path, media: FixtureMedia) -> DownloadService:
    identifiers = iter(f"incremental-run-{index}" for index in range(20))
    return DownloadService(
        FixtureDiscovery(),
        media,
        lambda: SQLiteUnitOfWork(repository / "catalog.sqlite3"),
        repository,
        clock=lambda: NOW,
        run_id_factory=lambda: next(identifiers),
    )


@pytest.mark.parametrize(
    ("existing", "requested", "new_indices"),
    [(0, 1, [0]), (1, 2, [1]), (2, 5, [2, 3, 4]), (4, 5, [4])],
)
def test_incremental_total_limit_downloads_only_remaining(
    tmp_path: Path, existing: int, requested: int, new_indices: list[int]
) -> None:
    repository = tmp_path / f"incremental-{existing}-{requested}"
    if existing:
        _service(repository, FixtureMedia()).execute(DownloadRequest("Reuters", existing))
    media = FixtureMedia()
    service = _incremental_service(repository, media)
    provider = IncrementalFixture([new_indices])

    result = service.execute_incremental(
        DownloadRequest("Reuters", requested), provider, 30, 2, lambda message: None
    )

    assert result.existing_before == existing
    assert result.downloaded_count == requested - existing
    assert result.total_after == requested
    assert result.complete is True
    assert len(list(repository.glob("profiles/*/posts/*/*/video.mp4"))) == requested
    manifest = json.loads((repository / "manifests/latest.json").read_text())
    assert manifest["requested_total"] == requested
    assert manifest["existing_before"] == existing
    assert manifest["downloaded_this_run"] == requested - existing
    assert manifest["total_after"] == requested
    assert manifest["complete"] is True


def test_incremental_complete_repository_performs_zero_discovery(tmp_path: Path) -> None:
    repository = tmp_path / "complete"
    _service(repository, FixtureMedia()).execute(DownloadRequest("Reuters", 5))
    provider = IncrementalFixture([])
    result = _incremental_service(repository, FixtureMedia()).execute_incremental(
        DownloadRequest("Reuters", 5), provider, 30, 2, lambda message: None
    )
    assert result.downloaded_count == 0
    assert result.total_after == 5
    assert provider.calls == []


def test_single_post_incremental_repeat_is_offline_idempotent(tmp_path: Path) -> None:
    repository = tmp_path / "single-post-repeat"
    _service(repository, FixtureMedia()).execute(DownloadRequest("Reuters", 1))
    provider = IncrementalFixture([])
    result = _incremental_service(repository, FixtureMedia()).execute_incremental(
        DownloadRequest("https://x.com/Reuters/status/9001?share=secret#fragment", 1),
        provider,
        30,
        1,
        lambda message: None,
    )
    assert result.downloaded_count == 0
    assert result.total_after == 1
    assert result.target == "https://x.com/Reuters/status/9001"
    assert provider.calls == []
    assert "secret" not in json.dumps(result.public_dict())
    manifest = (repository / "manifests/latest.json").read_text()
    assert '"target": "https://x.com/Reuters/status/9001"' in manifest
    assert "secret" not in manifest
    assert all("secret" not in path.read_text() for path in repository.rglob("metadata.json"))


def test_incremental_timeout_preserves_progress_and_second_attempt_completes(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "resume"
    provider = IncrementalFixture([[0], [1]], timeout=True)
    progress: list[str] = []
    result = _incremental_service(repository, FixtureMedia()).execute_incremental(
        DownloadRequest("Reuters", 2), provider, 30, 2, progress.append
    )
    assert result.downloaded_count == 2
    assert result.complete is True
    assert progress == [
        "discovery attempt 1/2",
        "downloaded 1/2",
        "discovery attempt 2/2",
        "downloaded 2/2",
    ]
    assert not list(repository.rglob("*.part"))
    assert not list(repository.rglob("*.tmp"))


def test_incremental_two_timeouts_preserve_incomplete_manifest(tmp_path: Path) -> None:
    repository = tmp_path / "partial"
    provider = IncrementalFixture([[0], []], timeout=True)
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        _incremental_service(repository, FixtureMedia()).execute_incremental(
            DownloadRequest("Reuters", 2), provider, 30, 2, lambda message: None
        )
    manifest = json.loads((repository / "manifests/latest.json").read_text())
    assert manifest["downloaded_this_run"] == 1
    assert manifest["total_after"] == 1
    assert manifest["complete"] is False
    assert len(list(repository.glob("profiles/*/posts/*/*/video.mp4"))) == 1


@pytest.mark.parametrize("limit", [1, 2, 5])
def test_downloads_exact_count_with_sidecars_manifest_catalog_and_idempotency(
    tmp_path: Path, limit: int
) -> None:
    repository = tmp_path / f"limit-{limit}"
    media = FixtureMedia()
    service = _service(repository, media)

    first = service.execute(DownloadRequest("Reuters", limit))

    assert first.downloaded_count == limit
    assert first.skipped_count == 0
    assert first.failed_count == 0
    assert media.part_observed
    videos = list(repository.glob("profiles/*/posts/*/*/video.mp4"))
    sidecars = list(repository.glob("profiles/*/posts/*/*/metadata.json"))
    assert len(videos) == len(sidecars) == limit
    assert not list(repository.rglob("*.part"))
    assert not list(repository.rglob("*.tmp"))

    manifest = json.loads((repository / "manifests/latest.json").read_text())
    assert manifest["downloaded_count"] == limit
    assert manifest["requested_limit"] == limit
    assert len(manifest["artifacts"]) == limit
    assert "signature=private" not in json.dumps(manifest)

    for video, sidecar_path in zip(sorted(videos), sorted(sidecars), strict=True):
        sidecar = json.loads(sidecar_path.read_text())
        digest = hashlib.sha256(video.read_bytes()).hexdigest()
        assert sidecar["schema_version"] == 1
        assert sidecar["sha256"] == digest
        assert sidecar["size_bytes"] == video.stat().st_size
        assert sidecar["relative_path"] == video.relative_to(repository).as_posix()
        assert "signature=private" not in json.dumps(sidecar)

    with sqlite3.connect(repository / "catalog.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM artifacts").fetchone() == (limit,)
        assert connection.execute(
            "SELECT COUNT(*) FROM download_jobs WHERE status='COMPLETED' AND attempts=1"
        ).fetchone() == (limit,)

    second = service.execute(DownloadRequest("Reuters", limit))
    assert second.downloaded_count == 0
    assert second.skipped_count == limit
    with sqlite3.connect(repository / "catalog.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM artifacts").fetchone() == (limit,)


def test_failure_removes_part_and_creates_no_artifact(tmp_path: Path) -> None:
    repository = tmp_path / "failure"
    service = _service(repository, FixtureMedia(fail=True))

    with pytest.raises(DownloadError, match="media download failed"):
        service.execute(DownloadRequest("Reuters", 1))

    assert not list(repository.rglob("*.part"))
    assert not list(repository.rglob("video.*"))
    manifest = json.loads((repository / "manifests/latest.json").read_text())
    assert manifest["failed_count"] == 1
    with sqlite3.connect(repository / "catalog.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM artifacts").fetchone() == (0,)
        assert connection.execute("SELECT status FROM download_jobs").fetchone() == (
            "FAILED_FINAL",
        )


def test_catalog_filesystem_conflict_fails_closed(tmp_path: Path) -> None:
    repository = tmp_path / "conflict"
    service = _service(repository, FixtureMedia())
    service.execute(DownloadRequest("Reuters", 1))
    video = next(repository.glob("profiles/*/posts/*/*/video.mp4"))
    video.write_bytes(b"tampered")

    with pytest.raises(DownloadConflictError, match="catalog and filesystem"):
        service.execute(DownloadRequest("Reuters", 1))


@pytest.mark.parametrize("limit", [0, 11])
def test_download_request_rejects_limit_outside_vertical_slice(limit: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 10"):
        DownloadRequest("Reuters", limit)
