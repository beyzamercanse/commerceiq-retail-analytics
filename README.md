# CommerceIQ — Enterprise Retail Analytics Engineering

[![CI](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml)

**Python ingestion → PostgreSQL → dbt warehouse → Streamlit BI → audited refresh**

A practical Analytics Engineering portfolio project illustrating transactional source ingestion, correct business grains, analytics marts and repeatable reporting checks.

## Built features

- **Ingestion:** Nine Olist CSV contracts, SHA-256 idempotency and raw lineage.
- **Transformations:** dbt staging, intermediate aggregates, customer/product/seller dimensions, facts and four marts.
- **Dashboards:** Five Streamlit pages covering revenue, retention, delivery, reconciliation and operations.
- **Operations:** Audited batch refreshes, data lineage, run history and recovery.
- **Quality:** Python, PostgreSQL, dbt and dashboard tests plus `commerceiq-audit` for independent aggregate checks.
- **Deployment preparation:** Streamlit Cloud dependency/config files, safe secrets template and separate read-only PostgreSQL role.

## Run locally

Prerequisites: Python 3.11+, Docker Compose, Git.

```bash
git clone https://github.com/beyzamercanse/commerceiq-retail-analytics.git
cd commerceiq-retail-analytics
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2'
docker compose up -d --wait
export DBT_PROFILES_DIR=analytics
commerceiq-refresh --data-dir data/sample_olist
commerceiq-audit --min-orders 3 --out artifacts/sample_audit.json
streamlit run dashboard/app.py
```

On Windows use PowerShell activation and `$env:DBT_PROFILES_DIR="analytics"`. Override `DBT_PASSWORD` when using non-default credentials.

**Bundled data is synthetic.** For a historical real-data run, download the original [Olist public dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), place its nine CSVs under `data/olist/`, then run:

```bash
commerceiq-refresh --data-dir data/olist
commerceiq-audit --min-orders 90000 --out artifacts/full_olist_audit.json
```

The minimum count is a coarse coverage check, **not proof of original data provenance**. Olist records are historical (2016–2018); merchandise value is not recognized revenue or profit.

## Warehouse grains

| Model | Grain |
|---|---|
| `fct_orders` | One order |
| `fct_order_items` | One order item |
| `fct_payments` | One payment entry |
| `dim_customers` | One stable customer identity |
| `mart_revenue_daily` | Purchase day |
| `mart_payment_reconciliation` | Order |
| `mart_customer_retention` | Cohort month × month offset |
| `mart_delivery_performance` | Purchase day |

**Critical design choice:** Item lines and split payments are aggregated separately to order grain to prevent multiplicative joins.

## Documentation

[Architecture](docs/architecture.md) · [Data contracts](docs/data-contracts.md) · [Warehouse](analytics/README.md) · [Operations](docs/operations.md) · [Deployment](docs/deployment.md) · [Interview demonstration](docs/demo_script.md) · [Roadmap](docs/roadmap.md)

**Deployment status:** Code is ready for Streamlit Community Cloud and an externally provisioned PostgreSQL database. No public dashboard URL, persistent database or full Olist verification has been established; CI uses temporary PostgreSQL and synthetic records.
