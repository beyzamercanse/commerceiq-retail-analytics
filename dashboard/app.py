"""Streamlit reporting UI for CommerceIQ dbt marts and pipeline audit records."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from commerceiq.config import database_url
from commerceiq.reporting import (
    ALLOWED_PAYMENTS,
    date_bounds,
    delivery_daily,
    overview,
    pipeline_history,
    reconciliation_details,
    reconciliation_summary,
    retention_cohorts,
    revenue_daily,
    source_health,
)


def money(value: object) -> str:
    return f"R$ {float(value or 0):,.2f}"


def selected_dates(first: date, last: date) -> tuple[date, date]:
    chosen = st.sidebar.date_input(
        "Purchase date range", value=(first, last), min_value=first, max_value=last
    )
    if not isinstance(chosen, tuple) or len(chosen) != 2:
        st.info("Select the start and end dates in the sidebar.")
        st.stop()
    return chosen


def revenue_page(dsn: str, start: date, end: date) -> None:
    st.subheader("Executive sales overview")
    st.caption(
        "BRL · Item value is gross merchandise value excluding freight; "
        "not recognized accounting revenue or profit."
    )
    metrics = overview(dsn, start, end)
    cols = st.columns(4)
    cols[0].metric("Orders", f"{metrics['orders']:,}")
    cols[1].metric("Item GMV", money(metrics["item_gmv_brl"]))
    cols[2].metric("Freight", money(metrics["freight_brl"]))
    cols[3].metric("Recorded payments", money(metrics["payments_brl"]))
    daily = pd.DataFrame(revenue_daily(dsn, start, end))
    if daily.empty:
        st.info("No orders for this range.")
        return
    daily = daily.set_index("purchase_date")
    chart = daily[["gross_item_value_brl", "recorded_payment_brl"]].astype(float)
    chart.columns = ["Item GMV", "Recorded payments"]
    st.line_chart(chart)
    st.markdown("**Orders and delivered orders**")
    st.bar_chart(daily[["order_count", "delivered_order_count"]])
    st.dataframe(daily.reset_index(), use_container_width=True, hide_index=True)


def retention_page(dsn: str) -> None:
    st.subheader("Customer retention by monthly cohort")
    st.caption(
        "Active means a non-canceled/non-unavailable purchase in the month. "
        "Month-zero customer count is each cohort's denominator."
    )
    data = pd.DataFrame(retention_cohorts(dsn))
    if data.empty:
        st.info("No eligible customer purchase history.")
        return
    matrix = data.pivot(
        index="cohort_month", columns="months_since_first_purchase", values="active_customers"
    ).sort_index()
    if 0 not in matrix.columns:
        st.warning("Month-zero cohort data is missing.")
        return
    retention = matrix.div(matrix[0].replace(0, float("nan")), axis=0).mul(100)
    retention.index = retention.index.astype(str)
    st.dataframe(
        retention.style.format("{:.1f}%", na_rep="—").background_gradient(
            cmap="Greens", axis=None, vmin=0, vmax=100
        ),
        use_container_width=True,
    )
    st.caption("Recent cohorts are right-censored, so later months may be unobserved.")
    st.markdown("**Cohort activity counts**")
    st.dataframe(matrix.reset_index(), use_container_width=True, hide_index=True)


def delivery_page(dsn: str, start: date, end: date) -> None:
    st.subheader("Delivery reliability")
    st.caption(
        "Late delivery = delivered after estimated date. "
        "Undelivered orders are excluded from the denominator."
    )
    daily = pd.DataFrame(delivery_daily(dsn, start, end))
    if daily.empty:
        st.info("No observations for this range.")
        return
    delivered = int(daily["delivered_count"].sum())
    late = int(daily["late_delivery_count"].sum())
    rate = 100 * late / delivered if delivered else None
    left, middle, right = st.columns(3)
    left.metric("Delivered", f"{delivered:,}")
    middle.metric("Late", f"{late:,}")
    right.metric("Late-delivery rate", f"{rate:.1f}%" if rate is not None else "N/A")
    daily["late_delivery_rate_pct"] = daily["late_delivery_rate"].astype(float) * 100
    st.line_chart(daily.set_index("purchase_date")["late_delivery_rate_pct"])
    st.dataframe(daily, use_container_width=True, hide_index=True)


def reconciliation_page(dsn: str, start: date, end: date) -> None:
    st.subheader("Order/payment reconciliation")
    st.caption(
        "Expected = item price + freight; recorded = all payment entries. "
        "A difference is an investigative signal, not confirmed revenue leakage."
    )
    summary = pd.DataFrame(reconciliation_summary(dsn, start, end))
    if not summary.empty:
        counts = summary.set_index("reconciliation_status")["orders"].to_dict()
        left, middle, right = st.columns(3)
        left.metric("Balanced", f"{counts.get('balanced', 0):,}")
        middle.metric("Investigate", f"{counts.get('investigate', 0):,}")
        other = sum(
            v for k, v in counts.items() if k not in {"balanced", "investigate"}
        )
        right.metric("Other statuses", f"{other:,}")
        st.bar_chart(summary.set_index("reconciliation_status")["orders"])
        st.dataframe(summary, use_container_width=True, hide_index=True)
    options = sorted(ALLOWED_PAYMENTS)
    selected_status = st.selectbox(
        "Investigate order records", options=options, index=options.index("investigate")
    )
    details = reconciliation_details(dsn, start, end, status=selected_status)
    if details:
        st.dataframe(pd.DataFrame(details), use_container_width=True, hide_index=True)
    else:
        st.info("No orders match this status in the selected period.")


def operations_page(dsn: str) -> None:
    st.subheader("Pipeline monitoring")
    st.caption(
        "Source timestamps reflect last ingestion, not market freshness. "
        "Historical Olist datasets are intentionally static."
    )
    sources = pd.DataFrame(source_health(dsn))
    if not sources.empty:
        left, right = st.columns(2)
        left.metric("Loaded source tables", len(sources))
        right.metric("Rows ingested across batches", f"{int(sources['rows_ingested'].sum()):,}")
        st.dataframe(sources, use_container_width=True, hide_index=True)
    st.markdown("**Audited refresh runs**")
    history = pd.DataFrame(pipeline_history(dsn))
    if history.empty:
        st.info("No refresh audit yet. Run commerceiq-refresh --data-dir data/sample_olist.")
    else:
        st.metric("Most recent refresh", str(history.iloc[0]["status"]).upper())
        st.dataframe(history, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="CommerceIQ | Retail Analytics", layout="wide")
    st.title("CommerceIQ")
    st.caption("Retail analytics engineering | PostgreSQL · dbt · Python")
    st.caption(
        "Data: Olist Brazilian E-Commerce (2016–2018), CC BY-NC-SA 4.0 — "
        "[original source](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)."
    )
    st.warning(
        "Results use your configured database. Bundled test CSVs are synthetic. "
        "This is not a live commerce or production system."
    )
    try:
        dsn = database_url()
        bounds = date_bounds(dsn)
        if bounds["first_date"] is None or bounds["last_date"] is None:
            st.info("No warehouse data. Ingest source CSVs and run dbt build first.")
            st.stop()
        first, last = selected_dates(bounds["first_date"], bounds["last_date"])
        page = st.sidebar.radio(
            "Explore",
            ["Revenue", "Customer retention", "Delivery performance", "Reconciliation", "Operations"],
        )
        if page == "Revenue":
            revenue_page(dsn, first, last)
        elif page == "Customer retention":
            retention_page(dsn)
        elif page == "Delivery performance":
            delivery_page(dsn, first, last)
        elif page == "Reconciliation":
            reconciliation_page(dsn, first, last)
        else:
            operations_page(dsn)
    except Exception as exc:  # noqa: BLE001 - sanitize UI errors at the app boundary
        # Avoid showing DSNs, which may contain database credentials.
        st.error(
            f"Reporting is unavailable ({type(exc).__name__}). "
            "Check PostgreSQL, DATABASE_URL, dbt build and DBT_SCHEMA."
        )
        st.stop()


if __name__ == "__main__":
    main()
