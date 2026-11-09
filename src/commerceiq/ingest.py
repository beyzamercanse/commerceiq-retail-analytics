"""Transactional, append-only CSV ingestion and source manifest."""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Iterator
from pathlib import Path

from commerceiq.sources import SOURCES, SourceSpec, source_files


def sha256_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def csv_records(path: Path, expected: tuple[str, ...]) -> Iterator[tuple[int, tuple[str, ...]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        actual = tuple(next(reader, ()))
        if actual != expected:
            raise ValueError(f"Schema mismatch in {path.name}. Expected {expected}; found {actual}")
        for row_index, fields in enumerate(reader, start=1):
            if len(fields) != len(expected):
                raise ValueError(
                    f"Malformed CSV record {row_index} in {path.name}: "
                    f"expected {len(expected)} values, received {len(fields)}"
                )
            yield row_index, tuple(fields)


def init_database(conn) -> None:
    from psycopg import sql

    with conn.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.source_files (
                source_name TEXT NOT NULL,
                file_sha256 CHAR(64) NOT NULL,
                file_name TEXT NOT NULL,
                row_count BIGINT NOT NULL CHECK (row_count >= 0),
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (source_name, file_sha256)
            )
        """)
        for spec in SOURCES:
            columns = sql.SQL(", ").join(
                sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in spec.columns
            )
            statement = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    _source_sha256 CHAR(64) NOT NULL,
                    _row_number INTEGER NOT NULL CHECK (_row_number > 0),
                    _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    {},
                    PRIMARY KEY (_source_sha256, _row_number)
                )
            """).format(sql.Identifier("raw", spec.table), columns)
            cursor.execute(statement)


def ingest_file(conn, spec: SourceSpec, path: Path) -> tuple[str, int]:
    """Return ('loaded'|'skipped', row count), treating a file as one transaction."""
    from psycopg import sql

    digest = sha256_file(path)
    with conn.transaction(), conn.cursor() as cursor:
        cursor.execute(
            "SELECT row_count FROM raw.source_files WHERE source_name=%s AND file_sha256=%s",
            (spec.table, digest),
        )
        previous = cursor.fetchone()
        if previous is not None:
            return "skipped", int(previous[0])

        columns = ["_source_sha256", "_row_number", *spec.columns]
        statement = sql.SQL("COPY {} ({}) FROM STDIN").format(
            sql.Identifier("raw", spec.table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
        )
        count = 0
        with cursor.copy(statement) as copy:
            for row_number, fields in csv_records(path, spec.columns):
                copy.write_row((digest, row_number, *fields))
                count += 1
        cursor.execute(
            """INSERT INTO raw.source_files (source_name, file_sha256, file_name, row_count)
               VALUES (%s, %s, %s, %s)""",
            (spec.table, digest, path.name, count),
        )
    return "loaded", count


def ingest_directory(dsn: str, data_dir: Path, *, strict: bool = False) -> list[tuple[str, str, int]]:
    import psycopg

    if not data_dir.is_dir():
        raise FileNotFoundError(f"Directory does not exist: {data_dir}")
    paths = source_files(data_dir, strict=strict)
    if not paths:
        raise FileNotFoundError(f"No recognized Olist CSV files found in {data_dir}")
    results = []
    with psycopg.connect(dsn, autocommit=True) as conn:
        init_database(conn)
        for spec, path in paths:
            status, count = ingest_file(conn, spec, path)
            results.append((spec.table, status, count))
    return results


def source_status(dsn: str) -> list[tuple[str, int, int]]:
    import psycopg

    with psycopg.connect(dsn) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT to_regclass('raw.source_files')")
        if cursor.fetchone()[0] is None:
            raise RuntimeError("Database is not initialized. Run: commerceiq init-db")
        cursor.execute("""
            SELECT source_name, count(*) AS files, sum(row_count) AS rows
            FROM raw.source_files GROUP BY source_name ORDER BY source_name
        """)
        return [(row[0], int(row[1]), int(row[2])) for row in cursor.fetchall()]
