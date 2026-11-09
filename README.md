# CommerceIQ — Enterprise Retail Analytics Engineering

[![CI](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml)

Portfolio data platform: **Python ingestion → PostgreSQL → dbt warehouse → Streamlit BI → audited refresh and monitoring**.

## Features

- **Ingestion:** original nine Olist CSV contracts, transactional batches, SHA-256 idempotency and load lineage.
- **Analytics:** dbt staging, intermediate one-order aggregation, customer/product/seller dimensions, order/item/payment facts and four marts.
- **Reporting:** five Streamlit pages — revenue, retention, delivery, reconciliation and operations.
- **Operations:** \`commerceiq-refresh\` orchestrates ingestion + dbt and records completion status, batch counts, duration timestamps and failure details.
- **Quality:** Python unit/integration tests, dbt generic and singular SQL tests, GitHub CI and reporting smoke checks.

## Quickstart (local)

Prerequisites: Python 3.11+, Docker Compose and Git.

\`\`\`bash
git clone https://github.com/beyzamercanse/commerceiq-retail-analytics.git
cd commerceiq-retail-analytics
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2'
docker compose up -d --wait
export DBT_PROFILES_DIR=analytics
commerceiq-refresh --data-dir data/sample_olist
streamlit run dashboard/app.py
\`\`\`

Open the local Streamlit URL printed in your terminal (normally http://localhost:8501).

**The included sample data is synthetic.** For real historical analysis, download the original [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), save the original CSVs to \`data/olist/\` (gitignored), then run:

\`\`\`bash
commerceiq-refresh --data-dir data/olist
\`\`\`

Olist data is historical, not a live retail feed. Reconciliation differences are not automatically lost revenue, and item merchandise value is not accounting-recognized revenue.

## Warehouse model grains

| Model | Grain |
|---|---|
| \`fct_orders\` | One order |
| \`fct_order_items\` | One order item |
| \`fct_payments\` | One payment entry |
| \`dim_customers\` | One stable customer identity |
| \`mart_revenue_daily\` | One purchase day |
| \`mart_payment_reconciliation\` | One order |
| \`mart_customer_retention\` | Cohort month × months after first purchase |
| \`mart_delivery_performance\` | One purchase day |

**Data grain safeguard:** order items and split payments are aggregated separately before joining at the order level.

## Run tests

\`\`\`bash
pytest
pytest -o addopts= -m integration
pytest -o addopts= -m reporting
dbt build --project-dir analytics
\`\`\`

The reporting tests require a built warehouse and an audited refresh. CI provisions a temporary Postgres instance and performs those steps in order.

## Documentation

- [Architecture](docs/architecture.md)
- [dbt model design](analytics/README.md)
- [Data contracts](docs/data-contracts.md)
- [Operations and recovery](docs/operations.md)
- [Project roadmap](docs/roadmap.md)

## Scope

This project is runnable locally. A deployed public dashboard, production database, persistent scheduler, and live monitoring are **not included**. GitHub Actions verifies each commit using disposable test infrastructure.
