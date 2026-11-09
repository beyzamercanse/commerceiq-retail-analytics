# CommerceIQ — deployment guide

**Deployment status:** prepared, not provisioned. The repository cannot create a cloud database or Streamlit Cloud app without the owner's account authorization.

## Architecture

- **Warehouse writer:** a separately credentialed PostgreSQL connection runs ingestion and dbt.
- **Dashboard reader:** separate PostgreSQL LOGIN with membership in `commerceiq_dashboard_reader`, with SELECT on mart tables and limited audit tables.
- **Dashboard host:** Streamlit Community Cloud executes `dashboard/app.py` using root `requirements.txt` and secrets stored only in the Streamlit app settings.

## Required setup

1. Provision a managed PostgreSQL database reachable over TLS. Check network allowlists, concurrent connection limits, storage, costs, and backup configuration. Local Docker PostgreSQL is not reachable from Community Cloud.
2. On your machine set `DATABASE_URL` to the **writer** connection (never commit it) and configure matching `DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_PASSWORD`, `DBT_DATABASE`, `DBT_SCHEMA`.
3. Install `python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2' kaggle`, download Olist from Kaggle (credentials are yours, not committed), and refresh:
   ```bash
   mkdir -p data/olist
   kaggle datasets download -d olistbr/brazilian-ecommerce -p data/olist --unzip
   commerceiq-refresh --data-dir data/olist
   commerceiq-audit --min-orders 90000 --out artifacts/full_olist_audit.json
   ```
   The threshold is a coarse sanity check, **not proof** of genuine provenance. Review results and dataset licensing.
4. In the cloud database, execute `deploy/readonly_role.sql` as the dbt table owner / privileged administrator. Create a *separate* login with a random strong password and give it membership in `commerceiq_dashboard_reader`. Verify that this login can SELECT mart tables but cannot INSERT, UPDATE, or access `raw.orders`.
5. Open [Streamlit Community Cloud](https://share.streamlit.io/) and select `beyzamercanse/commerceiq-retail-analytics`, branch `main`, entrypoint `dashboard/app.py`. Use Python 3.12.
6. Under **Advanced settings → Secrets**, enter:
   ```toml
   DATABASE_URL = "postgresql://dashboard_user:YOUR_PASSWORD@HOST:5432/commerceiq?sslmode=require"
   DBT_SCHEMA = "analytics"
   ```
   Save the secrets there, never in GitHub. The root-level secret variables are exposed to the Streamlit runtime as environment variables.
7. Deploy, verify Revenue/Retention/Delivery/Reconciliation/Operations pages, then save the actual URL in your portfolio. Do not invent a URL before the app exists.

## Validation checklist

- [ ] Hosted database writer and reader credentials separated
- [ ] Full Olist dataset loaded from the original publisher
- [ ] `commerceiq-audit` passes the full dataset threshold
- [ ] Reader cannot write or read source-level raw records
- [ ] TLS connection tested
- [ ] Deployed app visible publicly with appropriate source attribution
- [ ] Portfolio demo uses historical data clearly labeled 2016–2018
- [ ] Backups/cost/monitoring reviewed for hosted PostgreSQL

## Scheduling

Olist is a **static historical dataset**, so running a daily source refresh offers no business benefit. CI continues to validate code on every push. Once a changing source or a genuinely new data snapshot exists, introduce scheduled refreshes, alerting and retry policies against the persistent hosted database. Do not use a disposable CI PostgreSQL service as persistent storage.

## Privacy

Although the Olist dataset is anonymized, inspect the full dataset before publicly exposing order-level details. Do not share credentials, API tokens, private URLs, or personal/customer information in git, screenshots or audit artifacts.
