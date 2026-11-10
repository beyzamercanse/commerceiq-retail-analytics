"""Create reproducible, relationally consistent subsets of the historical Olist CSVs.

For constrained portfolio infrastructure, sample stable customer identities and
retain their orders and all associated item/payment/review records. This is NOT
representative random sampling of orders and must not be reported as full data.
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Callable
from pathlib import Path

from commerceiq.sources import SOURCES

SPEC_BY_FILE = {source.filename: source for source in SOURCES}


def stable_customer_selection(customer_unique_id: str, percent: int) -> bool:
    if not 1 <= percent <= 100:
        raise ValueError("Sample percentage must be between 1 and 100")
    digest = hashlib.sha256(customer_unique_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 100 < percent


def write_filtered(
    source_dir: Path,
    output_dir: Path,
    filename: str,
    predicate: Callable[[dict[str, str]], bool],
) -> int:
    spec = SPEC_BY_FILE[filename]
    source_file = source_dir / filename
    target_file = output_dir / filename
    count = 0
    with (
        source_file.open("r", encoding="utf-8-sig", newline="") as source_handle,
        target_file.open("w", encoding="utf-8", newline="") as output_handle,
    ):
        reader = csv.DictReader(source_handle)
        if tuple(reader.fieldnames or ()) != spec.columns:
            raise ValueError(f"Source schema mismatch for {filename}")
        writer = csv.DictWriter(output_handle, fieldnames=list(spec.columns))
        writer.writeheader()
        for row in reader:
            if predicate(row):
                writer.writerow(row)
                count += 1
    return count


def build_relational_sample(
    source_dir: Path,
    output_dir: Path,
    *,
    percent: int = 5,
) -> dict[str, int]:
    """Select customers by stable hash; preserve all of their related records.

    Geographic observations are reduced to one record per relevant ZIP prefix
    because they are not used by the business metric marts.
    """
    if not 1 <= percent <= 100:
        raise ValueError("Sample percentage must be between 1 and 100")
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Missing source directory: {source_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_customers: set[str] = set()
    selected_orders: set[str] = set()
    selected_products: set[str] = set()
    selected_sellers: set[str] = set()
    postal_prefixes: set[str] = set()

    def customer_filter(row: dict[str, str]) -> bool:
        selected = stable_customer_selection(row["customer_unique_id"], percent)
        if selected:
            selected_customers.add(row["customer_id"])
            postal_prefixes.add(row["customer_zip_code_prefix"])
        return selected

    counts = {
        "customers": write_filtered(
            source_dir, output_dir, "olist_customers_dataset.csv", customer_filter
        )
    }

    def order_filter(row: dict[str, str]) -> bool:
        if row["customer_id"] in selected_customers:
            selected_orders.add(row["order_id"])
            return True
        return False

    counts["orders"] = write_filtered(
        source_dir, output_dir, "olist_orders_dataset.csv", order_filter
    )

    def item_filter(row: dict[str, str]) -> bool:
        if row["order_id"] in selected_orders:
            selected_products.add(row["product_id"])
            selected_sellers.add(row["seller_id"])
            return True
        return False

    counts["order_items"] = write_filtered(
        source_dir, output_dir, "olist_order_items_dataset.csv", item_filter
    )
    counts["payments"] = write_filtered(
        source_dir, output_dir, "olist_order_payments_dataset.csv",
        lambda row: row["order_id"] in selected_orders,
    )
    counts["reviews"] = write_filtered(
        source_dir, output_dir, "olist_order_reviews_dataset.csv",
        lambda row: row["order_id"] in selected_orders,
    )
    counts["products"] = write_filtered(
        source_dir, output_dir, "olist_products_dataset.csv",
        lambda row: row["product_id"] in selected_products,
    )

    def seller_filter(row: dict[str, str]) -> bool:
        if row["seller_id"] in selected_sellers:
            postal_prefixes.add(row["seller_zip_code_prefix"])
            return True
        return False

    counts["sellers"] = write_filtered(
        source_dir, output_dir, "olist_sellers_dataset.csv", seller_filter
    )
    counts["category_translation"] = write_filtered(
        source_dir, output_dir, "product_category_name_translation.csv",
        lambda row: True,
    )

    seen_prefixes: set[str] = set()

    def geography_filter(row: dict[str, str]) -> bool:
        prefix = row["geolocation_zip_code_prefix"]
        if prefix in postal_prefixes and prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            return True
        return False

    counts["geolocation"] = write_filtered(
        source_dir, output_dir, "olist_geolocation_dataset.csv", geography_filter
    )
    return counts
