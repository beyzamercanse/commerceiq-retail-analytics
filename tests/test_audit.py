"""Pure audit contract tests."""
import pytest

from commerceiq.audit import evaluate


@pytest.fixture
def counts():
    return {
        "sources": 9, "raw_orders_unique": 3, "fact_orders": 3,
        "staging_items": 3, "fact_items": 3,
        "staging_payments": 3, "fact_payments": 3,
        "dated_fact_orders": 3, "daily_orders": 3,
        "dated_fact_item_value_cents": 13000, "daily_item_value_cents": 13000,
    }


def test_good_counts(counts):
    assert all(c.passed for c in evaluate(counts, min_orders=3))


def test_detects_fanout(counts):
    counts["fact_orders"] = 4
    assert any(c.name == "order_grain" and not c.passed for c in evaluate(counts))


def test_detects_bad_value(counts):
    counts["daily_item_value_cents"] = 12000
    assert any(c.name == "daily_item_value_cents" and not c.passed for c in evaluate(counts))


def test_rejects_negative_minimum(counts):
    with pytest.raises(ValueError):
        evaluate(counts, min_orders=-1)
