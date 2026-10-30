"""SQLite checkpoints and a recoverable Linux repository lock for B05."""

import fcntl
import sqlite3
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from types import TracebackType

from xma.adapters.catalog.migrations import migrate
from xma.domain.archive import (
    ArchiveMode,
    ArchiveRun,
    ArchiveStatus,
    CompletionReason,
)
from xma.domain.errors import CatalogError


def _stamp(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _date(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value.replace("Z", "+00:00"))


class SQLiteArchiveStore:
    def __init__(self, database: Path) -> None:
        self.database = database

    def initialize(self) -> None:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            migrate(connection)

    def latest(self) -> ArchiveRun | None:
        if not self.database.is_file():
            return None
        with sqlite3.connect(f"file:{self.database}?mode=ro", uri=True) as connection:
            connection.row_factory = sqlite3.Row
            try:
                row = connection.execute(
                    "SELECT r.*, c.next_allowed_at FROM archive_runs r "
                    "JOIN archive_checkpoints c USING(run_id) "
                    "ORDER BY r.created_at DESC LIMIT 1"
                ).fetchone()
            except sqlite3.OperationalError:
                return None
        return None if row is None else self._run(row)

    def put(self, run: ArchiveRun) -> None:
        self.initialize()
        with sqlite3.connect(self.database) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "INSERT INTO archive_runs (run_id,target_handle,requested_total,batch_size,"
                "request_interval_seconds,status,existing_before,downloaded_total,page_number,"
                "checkpoint_strategy,last_error_code,created_at,updated_at,completed_at,"
                "archive_mode,completion_reason,failed_total,max_items,max_runtime_seconds,"
                "min_free_space_bytes,resumed_at) VALUES "
                "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(run_id) DO UPDATE SET requested_total=excluded.requested_total, "
                "batch_size=excluded.batch_size, "
                "request_interval_seconds=excluded.request_interval_seconds, "
                "status=excluded.status, existing_before=excluded.existing_before, "
                "downloaded_total=excluded.downloaded_total, "
                "page_number=excluded.page_number, last_error_code=excluded.last_error_code, "
                "updated_at=excluded.updated_at, completed_at=excluded.completed_at, "
                "archive_mode=excluded.archive_mode, completion_reason=excluded.completion_reason, "
                "failed_total=excluded.failed_total, max_items=excluded.max_items, "
                "max_runtime_seconds=excluded.max_runtime_seconds, "
                "min_free_space_bytes=excluded.min_free_space_bytes, "
                "resumed_at=excluded.resumed_at",
                (
                    run.run_id,
                    run.target,
                    run.requested_total,
                    run.batch_size,
                    run.request_interval_seconds,
                    run.status.value,
                    run.existing_before,
                    run.downloaded_total,
                    run.page_number,
                    run.checkpoint_strategy,
                    run.last_error_code,
                    _stamp(run.created_at),
                    _stamp(run.updated_at),
                    None if run.completed_at is None else _stamp(run.completed_at),
                    run.mode.value,
                    None if run.completion_reason is None else run.completion_reason.value,
                    run.failed_total,
                    run.max_items,
                    run.max_runtime_seconds,
                    run.min_free_space_bytes,
                    None if run.resumed_at is None else _stamp(run.resumed_at),
                ),
            )
            connection.execute(
                "INSERT INTO archive_checkpoints VALUES (?,?,?,?,?) "
                "ON CONFLICT(run_id) DO UPDATE SET "
                "known_identity_count=excluded.known_identity_count, "
                "last_completed_page=excluded.last_completed_page, "
                "next_allowed_at=excluded.next_allowed_at, updated_at=excluded.updated_at",
                (
                    run.run_id,
                    run.downloaded_total,
                    run.page_number,
                    None if run.next_allowed_at is None else _stamp(run.next_allowed_at),
                    _stamp(run.updated_at),
                ),
            )

    @staticmethod
    def _run(row: sqlite3.Row) -> ArchiveRun:
        columns = set(row.keys())
        return ArchiveRun(
            row["run_id"],
            row["target_handle"],
            row["requested_total"],
            row["batch_size"],
            row["request_interval_seconds"],
            ArchiveStatus(row["status"]),
            row["existing_before"],
            row["downloaded_total"],
            row["page_number"],
            row["checkpoint_strategy"],
            _date(row["created_at"]),  # type: ignore[arg-type]
            _date(row["updated_at"]),  # type: ignore[arg-type]
            _date(row["completed_at"]),
            row["last_error_code"],
            _date(row["next_allowed_at"]),
            ArchiveMode(row["archive_mode"]) if "archive_mode" in columns else ArchiveMode.BOUNDED,
            None
            if "completion_reason" not in columns or row["completion_reason"] is None
            else CompletionReason(row["completion_reason"]),
            row["failed_total"] if "failed_total" in columns else 0,
            row["max_items"] if "max_items" in columns else None,
            row["max_runtime_seconds"] if "max_runtime_seconds" in columns else 3600,
            row["min_free_space_bytes"] if "min_free_space_bytes" in columns else 10 * 1024**3,
            _date(row["resumed_at"]) if "resumed_at" in columns else None,
        )


class RepositoryArchiveLock(AbstractContextManager["RepositoryArchiveLock"]):
    def __init__(self, repository: Path) -> None:
        self._path = repository / ".archive.lock"
        self._stream: object | None = None

    def __enter__(self) -> "RepositoryArchiveLock":
        self._path.parent.mkdir(parents=True, exist_ok=True)
        stream = self._path.open("a+")
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            stream.close()
            raise CatalogError("archive repository is already in use") from error
        self._stream = stream
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        assert self._stream is not None
        stream = self._stream
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]
        stream.close()  # type: ignore[attr-defined]
        self._stream = None
