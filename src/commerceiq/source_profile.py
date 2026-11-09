"""Standalone Olist CSV completeness and relationship inspection.

Designed to run before database ingestion. This verifies consistency and volume,
not the authenticity or licensing of an arbitrary dataset directory.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from commerceiq.ingest import sha256_file
from commerceiq.sources import SOURCES

KEYS = {
    "customers": ("customer_id",),
    "orders": ("order_id",),
    "order_items": ("order_id", "order_item_id"),
    "payments": ("order_id", "payment_sequential"),
    "reviews": ("review_id", "order_id"),
    "products": ("product_id",),
    "sellers": ("seller_id",),
    "category_translation": ("product_category_name",),
}

REFERENCES = (
    ("orders", "customer_id", "customers", "customer_id"),
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("order_items", "seller_id", "sellers", "seller_id"),
    ("payments", "order_id", "orders", "order_id"),
    ("reviews", "order_id", "orders", "order_id"),
)


def inspect_directory(folder: Path, *, min_orders: int = 1) -> dict:
    """Inspect all nine source files without storing individual row content in report."""
    if min_orders < 0:
        raise ValueError("min_orders must be non-negative")
    if not folder.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: {folder}")

    summaries: dict[str, dict] = {}
    observed: dict[tuple[str, str], set[str]] = defaultdict(set)
    failures: list[str] = []
    warnings: list[str] = []

    for spec in SOURCES:
        path = folder / spec.filename
        if not path.is_file():
            failures.append(f"Missing source CSV: {spec.filename}")
            continue

        seen_keys: set[tuple[str, ...]] = set()
        rows = duplicates = empty_keys = malformed = 0
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = tuple(next(reader, ()))
            if header != spec.columns:
                failures.append(f"Unexpected header: {spec.filename}")
                continue

            for line in reader:
                rows += 1
                if len(line) != len(header):
                    malformed += 1
                    continue
                record = dict(zip(header, line))
                key_columns = KEYS.get(spec.table)
                if key_columns:
                    key = tuple(record[column].strip() for column in key_columns)
                    if not all(key):
                        empty_keys += 1
                    elif key in seen_keys:
                        duplicates += 1
                    seen_keys.add(key)
                for source, field, target, other in REFERENCES:
                    if (spec.table == source and field in record) or (
                        spec.table == target and other in record
                    ):
                        chosen = field if spec.table == source else other
                        value = record[chosen].strip()
                        if value:
                            observed[(spec.table, chosen)].add(value)

        if malformed:
            failures.append(f"{spec.table}: {malformed} malformed records")
        if empty_keys:
            failures.append(f"{spec.table}: {empty_keys} rows with missing business keys")
        if duplicates:
            failures.append(f"{spec.table}: {duplicates} duplicate business keys")
        summaries[spec.table] = {
            "filename": spec.filename,
            "rows": rows,
            "sha256": sha256_file(path),
            "duplicate_business_keys": duplicates,
            "missing_business_keys": empty_keys,
            "malformed_records": malformed,
        }
        if rows == 0:
            warnings.append(f"{spec.table}: empty source table")

    for source, field, target, other in REFERENCES:
        if source not in summaries or target not in summaries:
            continue
        missing = observed[(source, field)] - observed[(target, other)]
        if missing:
            warnings.append(
                f"{source}.{field}: {len(missing)} distinct references absent from {target}.{other}"
            )

    orders = summaries.get("orders", {}).get("rows", 0)
    if orders < min_orders:
        failures.append(f"orders: {orders} rows below required minimum {min_orders}")

    return {
        "status": "pass" if not failures else "fail",
        "source": "user-supplied CSV directory; provenance not authenticated",
        "total_rows": sum(item["rows"] for item in summaries.values()),
        "order_rows": orders,
        "sources": summaries,
        "failures": failures,
        "warnings": warnings,
    }


def format_report(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True)
