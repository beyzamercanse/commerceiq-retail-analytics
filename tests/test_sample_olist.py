"""Relational sampling tests on the nine synthetic Olist CSV fixtures."""

import csv
from pathlib import Path

import pytest

from commerceiq.sample_olist import build_relational_sample, stable_customer_selection
from commerceiq.source_profile import inspect_directory

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_olist"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_full_percent_preserves_orders_and_payment_splits(tmp_path: Path):
    summary = build_relational_sample(DATA, tmp_path, percent=100)
    assert summary["orders"] == 3
    assert summary["order_items"] == 3
    assert summary["payments"] == 3
    assert inspect_directory(tmp_path, min_orders=3)["status"] == "pass"
    assert len(_read(tmp_path / "olist_order_payments_dataset.csv")) == 3


def test_hash_sampling_is_deterministic():
    assert stable_customer_selection("user-123", 7) == stable_customer_selection(
        "user-123", 7
    )
    assert stable_customer_selection("user-123", 100)


def test_subset_keeps_order_relationships(tmp_path: Path):
    build_relational_sample(DATA, tmp_path, percent=50)
    customers = {
        x["customer_id"] for x in _read(tmp_path / "olist_customers_dataset.csv")
    }
    orders = _read(tmp_path / "olist_orders_dataset.csv")
    order_ids = {row["order_id"] for row in orders}
    assert all(row["customer_id"] in customers for row in orders)
    for filename in (
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
    ):
        assert all(row["order_id"] in order_ids for row in _read(tmp_path / filename))


def test_invalid_percent(tmp_path: Path):
    with pytest.raises(ValueError):
        build_relational_sample(DATA, tmp_path, percent=0)
