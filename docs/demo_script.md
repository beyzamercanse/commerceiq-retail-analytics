# CommerceIQ — five-minute engineering interview demonstration

## 0:00–0:45 — Problem
Nine disparate order, customer, product, payment and delivery tables produce inconsistent reporting when joined naively. CommerceIQ is a reproducible ETL and dbt modeling project, not a deployed ERP or an accounting ledger.

## 0:45–1:30 — Architecture
Show `docs/architecture.md`: CSV → transactional Python ingestion / SHA-256 provenance → PostgreSQL → dbt staging → intermediate order-grain aggregations → facts/dimensions → Streamlit.

## 1:30–2:15 — Explain the fanout
Open `fct_order_items`, `fct_payments`, `int_order_item_totals`, and `int_order_payment_totals`. Explain why multiple items multiplied by split payments would overstate both amounts. Independently aggregate each child to order grain.

## 2:15–3:10 — Metrics
Show executive item GMV in BRL, fulfillment timeliness, monthly customer cohorts and reconciliation status. Explain exclusions and why GMV is **not recognized revenue**. Cohort retention is an observation, not a causal result.

## 3:10–4:00 — Reliability
Show one source manifest and `ops.pipeline_runs`. Run `commerceiq-refresh --data-dir data/sample_olist` twice: identical files are skipped. Describe how a dbt failure is logged and a rerun recovers.

## 4:00–5:00 — Audit and limitations
Run `commerceiq-audit --min-orders 3` and show GitHub Actions. Highlight the explicit tests covering fact grains and daily totals. Disclose whether dashboards show synthetic fixtures or full 2016–2018 Olist data; do not claim a hosted production service without an actual deployment.

## Interview prompts to prepare for

- Why does Olist have both `customer_id` and `customer_unique_id`?
- Which business grain prevents item/payment fanout?
- How would you handle refunds, delayed events, schema changes and incremental CDC?
- Why keep original data, source checksums, and audit runs?
- Which metrics require business sign-off?
- What would change if hundreds of millions of orders arrived continuously?
