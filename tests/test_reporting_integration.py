"""PostgreSQL/dbt end-to-end reporting smoke checks; run after dbt build."""

import os
from datetime import date
from decimal import Decimal

import pytest

from commerceiq.reporting import (
    date_bounds,
    delivery_daily,
    overview,
    pipeline_history,
    reconciliation_details,
    reconciliation_summary,
    retention_cohorts,
    revenue_daily,
    source_health,
)

pytestmark = pytest.mark.reporting


def test_sample_reporting_models():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        pytest.skip("DATABASE_URL is required")

    bounds = date_bounds(dsn)
    assert bounds["first_date"] == date(2018, 1, 1)
    assert bounds["last_date"] == date(2018, 2, 1)
    start, end = bounds["first_date"], bounds["last_date"]
    summary = overview(dsn, start, end)

    assert summary["orders"] == 3
    assert summary["items"] == 3
    assert summary["item_gmv_brl"] == Decimal("130.00")
    assert summary["payments_brl"] == Decimal("143.00")
    assert len(revenue_daily(dsn, start, end)) == 3

    delivery = delivery_daily(dsn, start, end)
    assert sum(int(row["delivered_count"]) for row in delivery) == 2

    reconciliation = reconciliation_summary(dsn, start, end)
    counts = {row["reconciliation_status"]: row["orders"] for row in reconciliation}
    assert counts["balanced"] == 2
    assert counts["no_items_or_payments"] == 1
    assert not reconciliation_details(dsn, start, end, status="investigate")

    cohorts = retention_cohorts(dsn)
    assert any(
        row["cohort_month"] == date(2018, 1, 1)
        and row["months_since_first_purchase"] == 1
        and row["active_customers"] == 1
        for row in cohorts
    )
    assert len(source_health(dsn)) == 9

    runs = pipeline_history(dsn)
    assert runs and runs[0]["status"] == "success"
    assert runs[0]["skipped_files"] == 9
