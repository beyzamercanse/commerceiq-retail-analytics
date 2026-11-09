"""Source contracts for the nine Olist CSVs; original column spellings retained."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceSpec:
    filename: str
    table: str
    columns: tuple[str, ...]


SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec("olist_customers_dataset.csv", "customers", (
        "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state")),
    SourceSpec("olist_orders_dataset.csv", "orders", (
        "order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date")),
    SourceSpec("olist_order_items_dataset.csv", "order_items", (
        "order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value")),
    SourceSpec("olist_order_payments_dataset.csv", "payments", (
        "order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value")),
    SourceSpec("olist_order_reviews_dataset.csv", "reviews", (
        "review_id", "order_id", "review_score", "review_comment_title", "review_comment_message",
        "review_creation_date", "review_answer_timestamp")),
    SourceSpec("olist_products_dataset.csv", "products", (
        "product_id", "product_category_name", "product_name_lenght", "product_description_lenght",
        "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm")),
    SourceSpec("olist_sellers_dataset.csv", "sellers", (
        "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state")),
    SourceSpec("olist_geolocation_dataset.csv", "geolocation", (
        "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state")),
    SourceSpec("product_category_name_translation.csv", "category_translation", (
        "product_category_name", "product_category_name_english")),
)


def source_files(data_dir: Path, *, strict: bool = False) -> list[tuple[SourceSpec, Path]]:
    available = [(spec, data_dir / spec.filename) for spec in SOURCES]
    missing = [str(path) for _, path in available if not path.is_file()]
    if strict and missing:
        raise FileNotFoundError("Missing required Olist files:\n" + "\n".join(missing))
    return [(spec, path) for spec, path in available if path.is_file()]
