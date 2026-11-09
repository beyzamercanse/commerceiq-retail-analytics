"""One-time guarded Olist data bootstrap for a private database service.

This command is intentionally not run by the public Streamlit web image.
"""

from __future__ import annotations

import os
from pathlib import Path

from commerceiq.audit import run_audit
from commerceiq.config import database_url
from commerceiq.ops import refresh
from commerceiq.source_profile import inspect_directory


def configure_dbt_from_pg_env() -> None:
    """Map standard PostgreSQL variables to this repository's dbt profile."""
    for key, fallback in (
        ("DBT_HOST", "PGHOST"),
        ("DBT_PORT", "PGPORT"),
        ("DBT_USER", "PGUSER"),
        ("DBT_PASSWORD", "PGPASSWORD"),
        ("DBT_DATABASE", "PGDATABASE"),
    ):
        if not os.getenv(key) and os.getenv(fallback):
            os.environ[key] = os.environ[fallback]


def main() -> None:
    if os.getenv("COMMERCEIQ_ALLOW_BOOTSTRAP") != "true":
        raise SystemExit("Set COMMERCEIQ_ALLOW_BOOTSTRAP=true to run the one-time load.")

    dsn = database_url()
    configure_dbt_from_pg_env()

    try:
        import kagglehub
    except ImportError as exc:
        raise SystemExit("Install kagglehub in the private worker image.") from exc

    directory = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
    validation = inspect_directory(directory, min_orders=90000)
    if validation["status"] != "pass":
        raise SystemExit("Original dataset failed local schema or duplicate-key validation.")

    run_id = refresh(
        dsn,
        directory,
        strict=True,
        project_dir=Path("analytics"),
        profiles_dir=Path("analytics"),
    )
    outcome = run_audit(dsn, min_orders=90000)
    if outcome["status"] != "pass":
        raise SystemExit("Loaded data failed the warehouse integrity audit.")

    print(f"Validated historical Olist dataset successfully. Refresh run_id={run_id}.")
    print(f"Loaded order count: {outcome['aggregate_counts']['fact_orders']}")
    print("This confirms consistency and minimum size, not independent source authenticity.")


if __name__ == "__main__":
    main()
