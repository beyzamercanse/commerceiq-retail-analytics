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


def provision_readonly_dashboard_role(dsn: str) -> None:
    """Create an isolated, least-privilege login from a securely supplied variable.

    Credentials are passed as SQL literals through psycopg composition and
    are never printed. The public Streamlit service must not receive the writer URL.
    """
    import psycopg
    from psycopg import sql

    password = os.getenv("COMMERCEIQ_DASHBOARD_PASSWORD")
    if not password or len(password) < 24:
        raise RuntimeError("COMMERCEIQ_DASHBOARD_PASSWORD must be at least 24 characters")

    role = sql.Identifier("commerceiq_dashboard")
    with psycopg.connect(dsn) as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = 'commerceiq_dashboard'"
        )
        if cursor.fetchone():
            cursor.execute(
                sql.SQL("ALTER ROLE {} LOGIN PASSWORD {}").format(
                    role, sql.Literal(password)
                )
            )
        else:
            cursor.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    role, sql.Literal(password)
                )
            )
        cursor.execute("GRANT USAGE ON SCHEMA analytics_marts, raw, ops TO commerceiq_dashboard")
        cursor.execute(
            "GRANT SELECT ON ALL TABLES IN SCHEMA analytics_marts TO commerceiq_dashboard"
        )
        cursor.execute("GRANT SELECT ON raw.source_files TO commerceiq_dashboard")
        cursor.execute("GRANT SELECT ON ops.pipeline_runs TO commerceiq_dashboard")
        cursor.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA analytics_marts "
            "GRANT SELECT ON TABLES TO commerceiq_dashboard"
        )
        cursor.execute(
            "SELECT has_table_privilege('commerceiq_dashboard', 'raw.orders', 'SELECT')"
        )
        if cursor.fetchone()[0]:
            raise RuntimeError("The read-only dashboard role unexpectedly has raw order access")


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

    provision_readonly_dashboard_role(dsn)

    print(f"Validated historical Olist dataset successfully. Refresh run_id={run_id}.")
    print(f"Loaded order count: {outcome['aggregate_counts']['fact_orders']}")
    print("This confirms consistency and minimum size, not independent source authenticity.")


if __name__ == "__main__":
    main()
