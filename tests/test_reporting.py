"""Pure input validation checks for SQL-backed reporting."""

import pytest

from commerceiq.reporting import marts_schema, reconciliation_details


def test_default_marts_schema(monkeypatch):
    monkeypatch.delenv("DBT_SCHEMA", raising=False)
    assert marts_schema() == "analytics_marts"


def test_custom_marts_schema(monkeypatch):
    monkeypatch.setenv("DBT_SCHEMA", "portfolio")
    assert marts_schema() == "portfolio_marts"


def test_invalid_schema_is_rejected(monkeypatch):
    monkeypatch.setenv("DBT_SCHEMA", 'analytics"; DROP TABLE public.x;--')
    with pytest.raises(ValueError, match="DBT_SCHEMA"):
        marts_schema()


def test_reconciliation_status_is_allowlisted():
    with pytest.raises(ValueError, match="Unrecognized reconciliation status"):
        reconciliation_details("dsn-unused", None, None, status="balanced' OR 1=1 --")


def test_reconciliation_limit_is_bounded():
    with pytest.raises(ValueError, match="detail limit"):
        reconciliation_details("dsn-unused", None, None, status="all", limit=10000)
