"""Warehouse audit with the disposable CI PostgreSQL and prebuilt dbt marts."""

import os

import pytest

from commerceiq.audit import run_audit

pytestmark = pytest.mark.reporting


def test_audit_passes_for_synthetic_fixture():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        pytest.skip("DATABASE_URL is required")
    report = run_audit(dsn, min_orders=3)
    assert report["status"] == "pass", report
    assert report["aggregate_counts"]["fact_orders"] == 3
    assert report["aggregate_counts"]["sources"] == 9
    assert report["dataset_scale"] == "sample_scale"
