# CommerceIQ dbt warehouse — Phase 2

## Run the models

After following the repository's PostgreSQL/Python quickstart and loading Olist CSVs:

\`\`\`bash
python -m pip install 'dbt-postgres>=1.9,<2'
export DBT_PROFILES_DIR=analytics
dbt debug --project-dir analytics
dbt build --project-dir analytics
dbt docs generate --project-dir analytics
dbt docs serve --project-dir analytics
\`\`\`

The profile uses \`DBT_HOST\`, \`DBT_PORT\`, \`DBT_USER\`, \`DBT_PASSWORD\`, \`DBT_DATABASE\`, \`DBT_SCHEMA\`. Default values match \`.env.example\`; override \`DBT_PASSWORD\` if your local credentials differ.

## Modeling contract

- **Raw**: source CSVs as text with source-file hashes; append-only.
- **Staging**: latest record per business key, cleaned and typed. Source keys intentionally retained.
- **Intermediate**: one order-level aggregate for item amounts, payments and reviews.
- **Marts**: dimensional entities, transaction facts, and business-facing daily/cohort/reconciliation outputs.

dbt's default PostgreSQL custom-schema behavior prefixes schema names with the target schema, so \`analytics_staging\`, \`analytics_intermediate\`, \`analytics_marts\` are expected.

### Correct business grain

- \`fct_orders\`: one row per order.
- \`fct_order_items\`: one row per (order_id, order_item_id).
- \`fct_payments\`: one row per (order_id, payment_sequential).
- \`dim_customers\`: one row per \`customer_unique_id\`, not order-specific \`customer_id\`.
- \`mart_revenue_daily\`: one row per purchase date.
- \`mart_customer_retention\`: one row per (cohort month, months since first purchase).

### Revenue accuracy

The source has **BRL**, not USD. The item subtotal excludes freight. Recorded payments can have splits or vouchers. Amounts are observed commerce amounts, **not accounting-recognized revenue**; refunds, chargebacks, coupons, cancellations, or fees may affect interpretation. Not all order/payment mismatches are erroneous. The reconciliation mart retains a status and raw differences for investigation.

### Source caveats

The free Olist dataset is historical (2016–2018). Staging deduplicates by source-ingestion time and row ordering; it is not an event-time CDC pipeline. A later backfill may overwrite the effective source record. Geolocation is averaged by postal prefix only for illustrative use and does not generate official coordinates.

## Validation

GitHub CI loads a small synthetic dataset with split payments (including a single order with two items), runs dbt compile, builds all analytics models, runs generic/singular tests, and generates docs. The CI data is a smoke test, not a substitute for checking full Olist data.

