# CommerceIQ — Enterprise Retail Analytics Engineering

**[Live Railway dashboard](https://commerceiq-dashboard-production.up.railway.app)** · PostgreSQL · dbt · Streamlit

Railway reports a successful web deployment and completed historical sample load: **5,081 Olist orders**. The hosted dataset represents a deterministic **5% customer sample**, not the full original Olist records. CI uses synthetic fixtures; hosted data comes from the historical public Kaggle dataset.


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

## Cloud deployment and source profiling

The repository now includes a Docker web image and a private loader image for Railway. `commerceiq-profile` checks the nine input CSVs for missing sources, unexpected headers, malformed records, duplicate business keys, and insufficient record volume.

```bash
commerceiq-profile --data-dir data/sample_olist --min-orders 3
# After obtaining the original Olist historical CSVs:
commerceiq-profile --data-dir data/olist --min-orders 90000 --out artifacts/source_profile.json
```

[Railway deployment playbook](docs/railway-deployment.md) · [Streamlit alternative](docs/deployment.md)

Original data source: [Olist Brazilian E-Commerce on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce); dataset license [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Public derived reports require attribution and license compliance.

**Railway deployment:** The starter free-plan database is limited to 500 MB, so the hosted option uses a deterministic ~5% sample of real historical Olist customers and their linked transactions. It is not the complete Olist dataset. Railway reports a running web service, verified port 8080, and successful source loading. External page access could not be independently checked from the assistant network. CI still uses synthetic fixtures.

**Deployment status:** Railway now hosts the public web service and a persistent private PostgreSQL database with a restricted dashboard login. The production database contains 5,081 original historical Olist order records selected by stable customer hashing. The complete Olist dataset has not been loaded and the assistant's external web checker could not fetch the public page.
