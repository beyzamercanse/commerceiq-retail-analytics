"""Audited local refresh: ingestion, dbt build, and run-level outcomes."""

from __future__ import annotations

import subprocess
from pathlib import Path

import psycopg

from commerceiq.ingest import ingest_directory


def initialize_audit(conn: psycopg.Connection) -> None:
    """Create refresh audit records without modifying the existing raw schemas."""
    with conn.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS ops")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
                run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                completed_at TIMESTAMPTZ,
                status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed')),
                input_directory TEXT NOT NULL,
                loaded_files INTEGER NOT NULL DEFAULT 0,
                skipped_files INTEGER NOT NULL DEFAULT 0,
                loaded_rows BIGINT NOT NULL DEFAULT 0,
                error_message TEXT
            )
        """)


def start_run(dsn: str, data_dir: Path) -> int:
    with psycopg.connect(dsn) as conn:
        initialize_audit(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO ops.pipeline_runs (status, input_directory)
                   VALUES ('running', %s) RETURNING run_id""",
                (str(data_dir),),
            )
            return int(cursor.fetchone()[0])


def finish_run(
    dsn: str,
    run_id: int,
    status: str,
    *,
    loaded_files: int = 0,
    skipped_files: int = 0,
    loaded_rows: int = 0,
    error_message: str | None = None,
) -> None:
    if status not in {"success", "failed"}:
        raise ValueError("Status must be 'success' or 'failed'")
    with psycopg.connect(dsn) as conn, conn.cursor() as cursor:
        cursor.execute(
            """UPDATE ops.pipeline_runs
               SET status = %s, completed_at = now(), loaded_files = %s,
                   skipped_files = %s, loaded_rows = %s, error_message = %s
               WHERE run_id = %s AND status = 'running'""",
            (
                status,
                loaded_files,
                skipped_files,
                loaded_rows,
                (error_message[:2000] if error_message else None),
                run_id,
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError(f"Pipeline run {run_id} was not running")


def refresh(
    dsn: str,
    data_dir: Path,
    *,
    strict: bool = True,
    project_dir: Path = Path("analytics"),
    profiles_dir: Path = Path("analytics"),
) -> int:
    """Run ingestion and dbt as one *audited job*, not one database transaction.

    A failed dbt build leaves the raw ingested batches available for replay.
    The next invocation safely skips identical input files by checksum.
    """
    run_id = start_run(dsn, data_dir)
    loaded = skipped = rows = 0
    try:
        results = ingest_directory(dsn, data_dir, strict=strict)
        loaded = sum(state == "loaded" for _, state, _ in results)
        skipped = sum(state == "skipped" for _, state, _ in results)
        rows = sum(count for _, state, count in results if state == "loaded")
        subprocess.run(
            [
                "dbt",
                "build",
                "--project-dir",
                str(project_dir.resolve()),
                "--profiles-dir",
                str(profiles_dir.resolve()),
            ],
            check=True,
        )
    except Exception as exc:
        finish_run(
            dsn,
            run_id,
            "failed",
            loaded_files=loaded,
            skipped_files=skipped,
            loaded_rows=rows,
            error_message=str(exc),
        )
        raise
    finish_run(
        dsn,
        run_id,
        "success",
        loaded_files=loaded,
        skipped_files=skipped,
        loaded_rows=rows,
    )
    return run_id
