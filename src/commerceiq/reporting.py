"""Read-only SQL service for Streamlit dashboards and operating checks."""

from __future__ import annotations

import os
from datetime import date

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

# The dbt-postgres default generate_schema_name macro prefixes custom schemas
# with the target schema, producing analytics_marts for the default profile.
ALLOWED_PAYMENTS = frozenset(
    {
        "all",
        "balanced",
        "investigate",
        "items_without_payments",
        "payment_without_items",
        "no_items_or_payments",
    }
)


def marts_schema() -> str:
    prefix = os.environ.get("DBT_SCHEMA", "analytics")
    if not prefix or not all(char.isascii() and (char.isalnum() or char == "_") for char in prefix):
        raise ValueError("DBT_SCHEMA must use simple ASCII letters, numbers or underscores")
    return f"{prefix}_marts"


def query(dsn: str, statement: str, params: tuple = ()) -> list[dict]:
    """Execute static parameterized SQL with an identifier-safe marts schema."""
    with psycopg.connect(dsn, row_factory=dict_row) as conn, conn.cursor() as cursor:
        cursor.execute(
            sql.SQL(statement).format(marts=sql.Identifier(marts_schema())),
            params,
        )
        return list(cursor.fetchall())


def date_bounds(dsn: str) -> dict:
    return query(
        dsn,
        """
        SELECT min(purchase_date) AS first_date,
               max(purchase_date) AS last_date
        FROM {marts}.mart_revenue_daily
        """,
    )[0]


def overview(dsn: str, start: date, end: date) -> dict:
    return query(
        dsn,
        """
        SELECT coalesce(sum(order_count), 0)::bigint AS orders,
               coalesce(sum(delivered_order_count), 0)::bigint AS delivered_orders,
               coalesce(sum(items_sold), 0)::bigint AS items,
               coalesce(sum(gross_item_value_brl), 0)::numeric AS item_gmv_brl,
               coalesce(sum(freight_value_brl), 0)::numeric AS freight_brl,
               coalesce(sum(recorded_payment_brl), 0)::numeric AS payments_brl
        FROM {marts}.mart_revenue_daily
        WHERE purchase_date BETWEEN %s AND %s
        """,
        (start, end),
    )[0]


def revenue_daily(dsn: str, start: date, end: date) -> list[dict]:
    return query(
        dsn,
        """
        SELECT purchase_date, order_count, delivered_order_count,
               gross_item_value_brl, freight_value_brl, recorded_payment_brl
        FROM {marts}.mart_revenue_daily
        WHERE purchase_date BETWEEN %s AND %s ORDER BY purchase_date
        """,
        (start, end),
    )


def retention_cohorts(dsn: str) -> list[dict]:
    return query(
        dsn,
        """
        SELECT cohort_month, months_since_first_purchase, active_customers
        FROM {marts}.mart_customer_retention
        ORDER BY cohort_month, months_since_first_purchase
        """,
    )


def delivery_daily(dsn: str, start: date, end: date) -> list[dict]:
    return query(
        dsn,
        """
        SELECT purchase_date, delivered_count, late_delivery_count, late_delivery_rate
        FROM {marts}.mart_delivery_performance
        WHERE purchase_date BETWEEN %s AND %s ORDER BY purchase_date
        """,
        (start, end),
    )


def reconciliation_summary(dsn: str, start: date, end: date) -> list[dict]:
    return query(
        dsn,
        """
        SELECT reconciliation_status, count(*)::bigint AS orders,
               coalesce(sum(abs(reconciliation_difference_brl)), 0) AS absolute_difference_brl
        FROM {marts}.mart_payment_reconciliation
        WHERE purchase_date BETWEEN %s AND %s
        GROUP BY reconciliation_status ORDER BY orders DESC, reconciliation_status
        """,
        (start, end),
    )


def reconciliation_details(
    dsn: str,
    start: date,
    end: date,
    status: str = "all",
    limit: int = 200,
) -> list[dict]:
    if status not in ALLOWED_PAYMENTS:
        raise ValueError(f"Unrecognized reconciliation status: {status}")
    if not 1 <= limit <= 1000:
        raise ValueError("The detail limit must be 1–1000")
    return query(
        dsn,
        """
        SELECT order_id, purchase_date, order_status, item_count, payment_count,
               expected_payment_brl, recorded_payment_brl, reconciliation_difference_brl,
               reconciliation_status
        FROM {marts}.mart_payment_reconciliation
        WHERE purchase_date BETWEEN %s AND %s
          AND (%s = 'all' OR reconciliation_status = %s)
        ORDER BY abs(reconciliation_difference_brl) DESC, order_id
        LIMIT %s
        """,
        (start, end, status, status, limit),
    )


def source_health(dsn: str) -> list[dict]:
    return query(
        dsn,
        """
        SELECT source_name, count(*)::bigint AS files,
               sum(row_count)::bigint AS rows_ingested,
               max(loaded_at) AS last_loaded_at
        FROM raw.source_files GROUP BY source_name ORDER BY source_name
        """,
    )


def pipeline_history(dsn: str, limit: int = 20) -> list[dict]:
    if not 1 <= limit <= 200:
        raise ValueError("Run history limit must be 1–200")
    return query(
        dsn,
        """
        SELECT run_id, started_at, completed_at, status, input_directory,
               loaded_files, skipped_files, loaded_rows, error_message
        FROM ops.pipeline_runs ORDER BY run_id DESC LIMIT %s
        """,
        (limit,),
    )
