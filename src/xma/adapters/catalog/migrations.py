"""Monotonic, reproducible SQLite schema migrations."""

import sqlite3
from importlib.resources import files

LATEST_SCHEMA_VERSION = 2


def _migration_sql(version: int) -> str:
    return (
        files("xma.adapters.catalog.schema")
        .joinpath("001_initial.sql" if version == 1 else "002_durable_archive.sql")
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


def migrate(connection: sqlite3.Connection) -> int:
    """Apply every pending migration in one explicit transaction."""
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
                (version, "2026-10-28T00:00:00.000000Z"),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return LATEST_SCHEMA_VERSION
