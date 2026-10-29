"""Standard-library SQLite implementation of the catalog port."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Literal, Self, cast

from xma.adapters.catalog.migrations import migrate
from xma.domain.enums import DownloadStatus, MediaType, PostType, RunStatus
from xma.domain.errors import CatalogError, IdentityConflictError
from xma.domain.models import Artifact, DiscoveryRun, DownloadJob, MediaAsset, Post, Profile


def _timestamp(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SQLiteCatalog:
    """Repository backed by a caller-owned SQLite connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def _insert(self, table: str, columns: tuple[str, ...], values: tuple[object, ...]) -> None:
        placeholders = ", ".join("?" for _ in values)
        names = ", ".join(columns)
        try:
            self._connection.execute(
                f"INSERT INTO {table} ({names}) VALUES ({placeholders})", values
            )
        except sqlite3.IntegrityError as error:
            raise IdentityConflictError(f"{table} identity conflicts with catalog") from error

    def put_profile(self, profile: Profile) -> None:
        existing = self.get_profile(profile.profile_id)
        if existing is None:
            self._insert(
                "profiles",
                ("profile_id", "handle", "display_name", "observed_at", "created_at", "updated_at"),
                (
                    profile.profile_id,
                    profile.handle,
                    profile.display_name,
                    _timestamp(profile.observed_at),
                    _timestamp(profile.created_at),
                    _timestamp(profile.updated_at),
                ),
            )
        elif existing.created_at != profile.created_at:
            raise IdentityConflictError("profiles identity conflicts with catalog")
        elif existing != profile:
            try:
                self._connection.execute(
                    "UPDATE profiles SET handle=?, display_name=?, observed_at=?, updated_at=? "
                    "WHERE profile_id=?",
                    (
                        profile.handle,
                        profile.display_name,
                        _timestamp(profile.observed_at),
                        _timestamp(profile.updated_at),
                        profile.profile_id,
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise IdentityConflictError("profiles identity conflicts with catalog") from error

    def get_profile(self, profile_id: str) -> Profile | None:
        row = self._connection.execute(
            "SELECT * FROM profiles WHERE profile_id=?", (profile_id,)
        ).fetchone()
        return (
            None
            if row is None
            else Profile(
                row["profile_id"],
                row["handle"],
                row["display_name"],
                _datetime(row["observed_at"]),
                _datetime(row["created_at"]),
                _datetime(row["updated_at"]),
            )
        )

    def put_post(self, post: Post) -> None:
        self._put_immutable(
            "posts",
            "post_id",
            post.post_id,
            post,
            ("post_id", "author_profile_id", "canonical_url", "text", "published_at", "post_type"),
            (
                post.post_id,
                post.author_profile_id,
                post.canonical_url,
                post.text,
                _timestamp(post.published_at),
                post.post_type.value,
            ),
            self.get_post,
        )

    def get_post(self, post_id: str) -> Post | None:
        row = self._one("posts", "post_id", post_id)
        return (
            None
            if row is None
            else Post(
                row["post_id"],
                row["author_profile_id"],
                row["canonical_url"],
                row["text"],
                _datetime(row["published_at"]),
                PostType(row["post_type"]),
            )
        )

    def put_media_asset(self, asset: MediaAsset) -> None:
        self._put_immutable(
            "media_assets",
            "asset_id",
            asset.asset_id,
            asset,
            (
                "asset_id",
                "post_id",
                "media_index",
                "media_type",
                "duration_ms",
                "width",
                "height",
                "variants_json",
            ),
            (
                asset.asset_id,
                asset.post_id,
                asset.media_index,
                asset.media_type.value,
                asset.duration_ms,
                asset.width,
                asset.height,
                json.dumps(asset.variants),
            ),
            self.get_media_asset,
        )

    def get_media_asset(self, asset_id: str) -> MediaAsset | None:
        row = self._one("media_assets", "asset_id", asset_id)
        return (
            None
            if row is None
            else MediaAsset(
                row["post_id"],
                row["media_index"],
                MediaType(row["media_type"]),
                row["duration_ms"],
                row["width"],
                row["height"],
                tuple(json.loads(row["variants_json"])),
            )
        )

    def put_discovery_run(self, run: DiscoveryRun) -> None:
        self._put_immutable(
            "discovery_runs",
            "run_id",
            run.run_id,
            run,
            (
                "run_id",
                "strategy",
                "started_at",
                "finished_at",
                "cursor",
                "discovered_count",
                "error_count",
                "status",
            ),
            (
                run.run_id,
                run.strategy,
                _timestamp(run.started_at),
                None if run.finished_at is None else _timestamp(run.finished_at),
                run.cursor,
                run.discovered_count,
                run.error_count,
                run.status.value,
            ),
            self.get_discovery_run,
        )

    def get_discovery_run(self, run_id: str) -> DiscoveryRun | None:
        row = self._one("discovery_runs", "run_id", run_id)
        return (
            None
            if row is None
            else DiscoveryRun(
                row["run_id"],
                row["strategy"],
                _datetime(row["started_at"]),
                RunStatus(row["status"]),
                None if row["finished_at"] is None else _datetime(row["finished_at"]),
                row["cursor"],
                row["discovered_count"],
                row["error_count"],
            )
        )

    def put_download_job(self, job: DownloadJob) -> None:
        existing = self.get_download_job(job.job_id)
        if existing is None:
            self._insert(
                "download_jobs",
                (
                    "job_id",
                    "asset_id",
                    "run_id",
                    "status",
                    "attempts",
                    "error_code",
                    "error_message",
                    "created_at",
                    "updated_at",
                ),
                (
                    job.job_id,
                    job.asset_id,
                    job.run_id,
                    job.status.value,
                    job.attempts,
                    job.error_code,
                    job.error_message,
                    _timestamp(job.created_at),
                    _timestamp(job.updated_at),
                ),
            )
        elif (
            existing.asset_id != job.asset_id
            or existing.run_id != job.run_id
            or existing.created_at != job.created_at
        ):
            raise IdentityConflictError("download_jobs identity conflicts with catalog")
        elif existing != job:
            try:
                expected = existing.transition(
                    job.status,
                    job.updated_at,
                    error_code=job.error_code,
                    error_message=job.error_message,
                )
            except ValueError as error:
                raise IdentityConflictError(
                    "download_jobs update is not a valid transition"
                ) from error
            if expected != job:
                raise IdentityConflictError("download_jobs update is not a valid transition")
            self._connection.execute(
                "UPDATE download_jobs SET status=?, attempts=?, error_code=?, error_message=?, "
                "updated_at=? WHERE job_id=?",
                (
                    job.status.value,
                    job.attempts,
                    job.error_code,
                    job.error_message,
                    _timestamp(job.updated_at),
                    job.job_id,
                ),
            )

    def get_download_job(self, job_id: str) -> DownloadJob | None:
        row = self._one("download_jobs", "job_id", job_id)
        return (
            None
            if row is None
            else DownloadJob(
                row["job_id"],
                row["asset_id"],
                row["run_id"],
                DownloadStatus(row["status"]),
                row["attempts"],
                _datetime(row["created_at"]),
                _datetime(row["updated_at"]),
                row["error_code"],
                row["error_message"],
            )
        )

    def list_download_jobs(self) -> tuple[DownloadJob, ...]:
        rows = self._connection.execute(
            "SELECT job_id FROM download_jobs ORDER BY job_id"
        ).fetchall()
        return tuple(
            job for row in rows if (job := self.get_download_job(row["job_id"])) is not None
        )

    def put_artifact(self, artifact: Artifact) -> None:
        self._put_immutable(
            "artifacts",
            "artifact_id",
            artifact.artifact_id,
            artifact,
            (
                "artifact_id",
                "job_id",
                "relative_path",
                "mime_type",
                "size_bytes",
                "sha256",
                "created_at",
            ),
            (
                artifact.artifact_id,
                artifact.job_id,
                artifact.relative_path,
                artifact.mime_type,
                artifact.size_bytes,
                artifact.sha256,
                _timestamp(artifact.created_at),
            ),
            self.get_artifact,
        )

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        row = self._one("artifacts", "artifact_id", artifact_id)
        return (
            None
            if row is None
            else Artifact(
                row["artifact_id"],
                row["job_id"],
                row["relative_path"],
                row["mime_type"],
                row["size_bytes"],
                row["sha256"],
                _datetime(row["created_at"]),
            )
        )

    def list_artifacts(self) -> tuple[Artifact, ...]:
        rows = self._connection.execute(
            "SELECT artifact_id FROM artifacts ORDER BY artifact_id"
        ).fetchall()
        return tuple(
            artifact
            for row in rows
            if (artifact := self.get_artifact(row["artifact_id"])) is not None
        )

    def _one(self, table: str, key: str, value: str) -> sqlite3.Row | None:
        return cast(
            sqlite3.Row | None,
            self._connection.execute(f"SELECT * FROM {table} WHERE {key}=?", (value,)).fetchone(),
        )

    def _put_immutable(
        self,
        table: str,
        key: str,
        value: str,
        entity: object,
        columns: tuple[str, ...],
        values: tuple[object, ...],
        getter: object,
    ) -> None:
        current = getter(value)  # type: ignore[operator]
        if current is None:
            self._insert(table, columns, values)
        elif current != entity:
            raise IdentityConflictError(f"{table} identity conflicts with catalog")


class SQLiteUnitOfWork:
    """Explicit transaction boundary with deterministic connection cleanup."""

    def __init__(self, database: str | Path) -> None:
        self._database = str(database)
        self._connection: sqlite3.Connection | None = None
        self.catalog: SQLiteCatalog

    def __enter__(self) -> Self:
        connection = sqlite3.connect(self._database, isolation_level=None)
        connection.execute("PRAGMA foreign_keys = ON")
        migrate(connection)
        connection.execute("BEGIN")
        self._connection = connection
        self.catalog = SQLiteCatalog(connection)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        assert self._connection is not None
        try:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        except sqlite3.Error as error:
            raise CatalogError("could not close catalog transaction") from error
        finally:
            self._connection.close()
            self._connection = None
        return False


@contextmanager
def open_catalog(database: str | Path) -> Iterator[SQLiteCatalog]:
    with SQLiteUnitOfWork(database) as unit_of_work:
        yield unit_of_work.catalog
