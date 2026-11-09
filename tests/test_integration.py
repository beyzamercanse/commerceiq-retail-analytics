"""PostgreSQL integration test, enabled explicitly or by CI."""
import os
from pathlib import Path

import pytest

from commerceiq.ingest import ingest_directory, init_database

psycopg = pytest.importorskip("psycopg")


@pytest.mark.integration
def test_sample_ingestion_is_idempotent():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        pytest.skip("Set DATABASE_URL to run database integration tests")

    sample = Path(__file__).resolve().parents[1] / "data" / "sample_olist"
    with psycopg.connect(dsn) as conn:
        init_database(conn)
    first = ingest_directory(dsn, sample, strict=True)
    second = ingest_directory(dsn, sample, strict=True)
    assert len(first) == len(second) == 9
    assert all(item[1] == "skipped" for item in second)
    with psycopg.connect(dsn) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM raw.orders")
        assert cursor.fetchone()[0] >= 3
        cursor.execute("SELECT COUNT(*) FROM raw.source_files WHERE source_name='orders'")
        assert cursor.fetchone()[0] >= 1
