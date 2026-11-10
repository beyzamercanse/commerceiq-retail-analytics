"""Ensure the public service uses the read-only account and populated marts."""

from __future__ import annotations

import os
import sys

import psycopg


def permissions_ok(role: str, can_read_marts: bool, can_write: bool, can_read_raw: bool) -> bool:
    return (
        role == "commerceiq_dashboard"
        and can_read_marts
        and not can_write
        and not can_read_raw
    )


def main() -> None:
    # Do not print database connection strings or raw psycopg errors.
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        sys.exit("CommerceIQ readiness failed: DATABASE_URL is not configured")

    try:
        with psycopg.connect(dsn, connect_timeout=10) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT current_user,
                    has_table_privilege(current_user, 'analytics_marts.fct_orders', 'SELECT'),
                    has_table_privilege(current_user, 'analytics_marts.fct_orders', 'INSERT'),
                    has_table_privilege(current_user, 'raw.orders', 'SELECT')
                """
            )
            role, can_read_marts, can_write, can_read_raw = cur.fetchone()
            if not permissions_ok(role, can_read_marts, can_write, can_read_raw):
                sys.exit("CommerceIQ readiness failed: dashboard login is not least-privilege")
            cur.execute("SELECT count(*) FROM analytics_marts.fct_orders")
            count = int(cur.fetchone()[0])
            if count < 1000:
                sys.exit("CommerceIQ readiness failed: expected historical sample is missing")
    except psycopg.Error:
        sys.exit("CommerceIQ readiness failed: read-only warehouse connection unavailable")

    print(f"CommerceIQ ready: read-only role verified; {count:,} historical orders")


if __name__ == "__main__":
    main()
