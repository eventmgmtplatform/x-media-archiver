"""Offline tests for the B04 download vertical slice."""

import hashlib
import json
import sqlite3
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
from xma.domain.errors import DomainError, DownloadConflictError, DownloadError

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


@pytest.mark.parametrize("limit", [0, 6])
def test_download_request_rejects_limit_outside_vertical_slice(limit: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 5"):
        DownloadRequest("Reuters", limit)
