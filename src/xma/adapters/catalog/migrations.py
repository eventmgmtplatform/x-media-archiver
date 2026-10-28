"""Monotonic, reproducible SQLite schema migrations."""

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.resources import files

LATEST_SCHEMA_VERSION = 1


def _migration_sql(version: int) -> str:
    return (
        files("xma.adapters.catalog.schema")
        .joinpath(f"{version:03d}_initial.sql")
        .read_text(encoding="utf-8")
    )


def _statements(script: str) -> list[str]:
    statements: list[str] = []
    pending = ""
    for character in script:
        pending += character
        if character == ";" and sqlite3.complete_statement(pending):
            statements.append(pending.strip())
            pending = ""
    if pending.strip():
        raise RuntimeError("migration contains an incomplete SQL statement")
    return statements


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("migration clock must return a timezone-aware datetime")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def migrate(connection: sqlite3.Connection, *, now: Callable[[], datetime] | None = None) -> int:
    """Apply every pending migration in one explicit transaction."""
    clock = now if now is not None else lambda: datetime.now(UTC)
    try:
        connection.execute("BEGIN")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_version "
            "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        row = connection.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()
        current = int(row[0])
        if current > LATEST_SCHEMA_VERSION:
            raise RuntimeError(f"catalog schema {current} is newer than supported version")
        for version in range(current + 1, LATEST_SCHEMA_VERSION + 1):
            for statement in _statements(_migration_sql(version)):
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_version(version, applied_at) VALUES (?, ?)",
                (version, _utc_timestamp(clock())),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return LATEST_SCHEMA_VERSION
