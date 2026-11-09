"""Verify the optional dashboard reader role has no write or raw-order privileges."""

import os
from pathlib import Path

import psycopg
import pytest

pytestmark = pytest.mark.reporting


def test_dashboard_reader_permissions():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        pytest.skip("Requires a test PostgreSQL database")
    ddl = Path(__file__).resolve().parents[1] / "deploy" / "readonly_role.sql"
    with psycopg.connect(dsn) as conn, conn.cursor() as cursor:
        cursor.execute(ddl.read_text(encoding="utf-8"))
        cursor.execute(
            """
            SELECT has_table_privilege('commerceiq_dashboard_reader',
                                       'analytics_marts.fct_orders', 'SELECT'),
                   has_table_privilege('commerceiq_dashboard_reader',
                                       'analytics_marts.fct_orders', 'INSERT'),
                   has_table_privilege('commerceiq_dashboard_reader',
                                       'raw.orders', 'SELECT'),
                   has_table_privilege('commerceiq_dashboard_reader',
                                       'ops.pipeline_runs', 'SELECT')
            """
        )
        assert cursor.fetchone() == (True, False, False, True)
