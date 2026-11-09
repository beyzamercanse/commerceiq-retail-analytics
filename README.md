# CommerceIQ — Enterprise Retail Analytics Engineering

An end-to-end portfolio project demonstrating Python-based ingestion, PostgreSQL raw storage, data provenance, tests, and CI. **Phase 1 implemented**; dbt analytics models and dashboards are planned, not yet built.

![CI](https://github.com/beyzamercanse/commerceiq-retail-analytics/actions/workflows/ci.yml/badge.svg)

## Run locally

Prerequisites: Python 3.11+, Docker with Compose, Git.

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
docker compose up -d --wait
commerceiq ingest --data-dir data/sample_olist --strict
commerceiq status
pytest
```

Re-running ingestion skips identical files by SHA-256. Sample CSV files are synthetic (not actual Olist data).

## Full dataset

Download the [Olist Brazilian E-Commerce public dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place its nine CSV files in `data/olist/` (gitignored). Then run:

```bash
commerceiq sources
commerceiq ingest --data-dir data/olist --strict
commerceiq status
```

## Data flow

```text
Original Olist CSVs -> schema-validated Python ingestion -> PostgreSQL raw.*
                             |                         |
                        SHA-256 checksum          source_files audit log
```

Every row stores source checksum, original row number, and loading timestamp. Raw fields retain text representations; business typing and reconciliation will be implemented with dbt in Phase 2.

**Design warning:** orders have multiple items and payments. Joining items and payments without aggregation to compatible grains inflates revenue.

## Roadmap

1. **Phase 1 (code committed)**: Python CSV ingestion, PostgreSQL schema, transactional loads, tests, CI.
2. **Phase 2 (planned)**: dbt staging, intermediate models, facts/dimensions, data quality.
3. **Phase 3 (planned)**: semantic KPI marts, BI dashboards, scheduling and monitoring.

This is a portfolio demonstration, not production-ready software. CI integration tests use disposable PostgreSQL; local end-to-end setup also requires Docker.