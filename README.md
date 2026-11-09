# CommerceIQ — Enterprise Retail Analytics Engineering

End-to-end retail data platform: **Python ingestion → PostgreSQL raw tables → dbt analytics warehouse → BI dashboards (planned)**.

![CI](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml/badge.svg)

## Implemented

**Phase 1:** nine Olist source contracts, transactional Python CSV ingestion, source-file hashes, PostgreSQL storage, unit/integration tests and CI.

**Phase 2:** dbt staging (deduplication, casting), intermediate per-order aggregations, dimensional models, line-level facts, daily retail metrics, cohort retention, delivery performance, and payment reconciliation, with SQL tests and CI warehouse build.

**Phase 3 planned:** dashboards, scheduling, pipeline monitoring, cloud serving.

## Local quickstart

Prerequisites: Python 3.11+, Docker Compose, Git.

\`\`\`bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' 'dbt-postgres>=1.9,<2'
docker compose up -d --wait
commerceiq ingest --data-dir data/sample_olist --strict
commerceiq status
pytest
export DBT_PROFILES_DIR=analytics
dbt debug --project-dir analytics
dbt build --project-dir analytics
dbt docs generate --project-dir analytics
\`\`\`

If your database password is not the default, export matching \`DBT_PASSWORD\`.

The bundled sample dataset is synthetic, not actual Olist data. For the real dataset download [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place nine original CSVs into \`data/olist/\` (ignored by Git):

\`\`\`bash
commerceiq ingest --data-dir data/olist --strict
dbt build --project-dir analytics
\`\`\`

See [analytics/README.md](analytics/README.md) for model grains and caveats, [architecture](docs/architecture.md), [data contracts](docs/data-contracts.md), and [roadmap](docs/roadmap.md).

## Example warehouse models

| Model | Business grain |
|---|---|
| \`fct_orders\` | One row per order |
| \`fct_order_items\` | One order item |
| \`fct_payments\` | One payment sequence |
| \`dim_customers\` | One stable customer identity |
| \`mart_revenue_daily\` | One purchase date |
| \`mart_payment_reconciliation\` | One order |
| \`mart_customer_retention\` | Cohort × month offset |

**Double-count protection:** Item facts and payment facts are never joined directly. They are aggregated independently at order grain before being reconciled. Purchase subtotal is **not** GAAP/IFRS revenue and payment differences are investigative signals, not necessarily loss.

