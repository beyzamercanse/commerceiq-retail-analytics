"""Read-only warehouse checks with aggregate-only JSON results."""
from __future__ import annotations

from dataclasses import asdict, dataclass

import psycopg
from psycopg import sql

from commerceiq.reporting import marts_schema
from commerceiq.sources import SOURCES


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    actual: int
    expected: int
    description: str


def evaluate(counts: dict[str, int], min_orders: int = 1) -> list[Check]:
    if min_orders < 0:
        raise ValueError("min_orders must be nonnegative")
    contract = [
        ("sources", "sources", len(SOURCES), "Source manifest coverage"),
        ("order_grain", "fact_orders", counts["raw_orders_unique"], "Orders preserve distinct source keys"),
        ("item_grain", "fact_items", counts["staging_items"], "Item fact has expected grain"),
        ("payment_grain", "fact_payments", counts["staging_payments"], "Payment fact has expected grain"),
        ("daily_orders", "daily_orders", counts["dated_fact_orders"], "Daily order mart matches facts"),
        ("daily_item_value_cents", "daily_item_value_cents",
         counts["dated_fact_item_value_cents"], "Item value reconciles in BRL cents"),
    ]
    checks = [
        Check(name, counts[key] == expected, counts[key], expected, description)
        for name, key, expected, description in contract
    ]
    checks.append(Check("minimum_orders", counts["fact_orders"] >= min_orders,
                        counts["fact_orders"], min_orders, "Minimum required sample size"))
    return checks


def run_audit(dsn: str, *, min_orders: int = 1) -> dict:
    prefix = marts_schema().removesuffix("_marts")
    marts = sql.Identifier(prefix + "_marts")
    staging = sql.Identifier(prefix + "_staging")
    queries = {
        "sources": "SELECT count(DISTINCT source_name) FROM raw.source_files",
        "raw_orders_unique": "SELECT count(DISTINCT nullif(btrim(order_id), '')) FROM raw.orders",
        "fact_orders": "SELECT count(*) FROM {marts}.fct_orders",
        "staging_items": "SELECT count(*) FROM {staging}.stg_order_items",
        "fact_items": "SELECT count(*) FROM {marts}.fct_order_items",
        "staging_payments": "SELECT count(*) FROM {staging}.stg_payments",
        "fact_payments": "SELECT count(*) FROM {marts}.fct_payments",
        "dated_fact_orders": (
            "SELECT count(*) FROM {marts}.fct_orders WHERE purchase_date IS NOT NULL"
        ),
        "daily_orders": "SELECT coalesce(sum(order_count), 0) FROM {marts}.mart_revenue_daily",
        "dated_fact_item_value_cents": (
            "SELECT coalesce(round(sum(item_subtotal_brl) * 100), 0)::bigint "
            "FROM {marts}.fct_orders WHERE purchase_date IS NOT NULL"
        ),
        "daily_item_value_cents": (
            "SELECT coalesce(round(sum(gross_item_value_brl) * 100), 0)::bigint "
            "FROM {marts}.mart_revenue_daily"
        ),
    }
    counts = {}
    with psycopg.connect(dsn) as connection, connection.cursor() as cursor:
        with connection.transaction():
            cursor.execute("SET TRANSACTION READ ONLY")
            for name, statement in queries.items():
                cursor.execute(sql.SQL(statement).format(marts=marts, staging=staging))
                counts[name] = int(cursor.fetchone()[0])
    checks = evaluate(counts, min_orders=min_orders)
    return {
        "status": "pass" if all(c.passed for c in checks) else "fail",
        "checks": [asdict(c) for c in checks],
        "aggregate_counts": counts,
        "dataset_scale": "sample_scale" if counts["fact_orders"] < 1000 else "large_scale",
        "note": "Dataset scale does not verify source authenticity.",
    }
