# CommerceIQ — Railway deployment playbook

**Current status: code is prepared, but no Railway project, database or public domain has been provisioned.**

## Why two services?

The dashboard is a read-only Streamlit application; a separate one-off worker ingests source data and runs dbt. PostgreSQL stays private inside Railway. Avoid using owner/database-superuser credentials for the public-facing dashboard.

- **Database:** PostgreSQL service with persistent volume and backups appropriate to your plan.
- **Loader:** private service built from `Dockerfile.worker`, executed once after provisioning PostgreSQL.
- **Web:** public service built from root `Dockerfile`, with Streamlit bound to Railway's `PORT`.

## Setup after Railway is connected

1. Create a Railway project. Review its billing, storage and network costs before activating resources.
2. Add PostgreSQL to the project. Keep public TCP access disabled. Railway documents `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` and `DATABASE_URL` for connecting services.
3. Create a one-off **private loader** service from this GitHub repository. Set its **Dockerfile path** to `Dockerfile.worker`. Set `DATABASE_URL` to the database's internal URL and reference the standard `PG*` values from the PostgreSQL service. Set `COMMERCEIQ_ALLOW_BOOTSTRAP=true`.
4. Run the loader only when intended; it downloads the original public Olist dataset via KaggleHub, validates the nine CSVs and minimum order count, ingests PostgreSQL, runs dbt, and checks aggregate warehouse reconciliation. The job can use significant database storage and CPU. Do not add a recurring schedule for static historical data.
5. In PostgreSQL, apply `deploy/readonly_role.sql` as the table owner. Create a separate dashboard LOGIN with a strong generated password and grant it membership in `commerceiq_dashboard_reader`. Verify SELECT works for marts and fails for `raw.orders` and INSERT operations.
6. Create a **web** service from the same repository. Railway finds root `Dockerfile` automatically. Set its `DATABASE_URL` to the dashboard read-only login URL using Railway private networking. Set `DBT_SCHEMA=analytics`; never use the loader's database credentials in the web service.
7. Enable public networking for **the web service only**, not PostgreSQL or the loader. Check `/_stcore/health`, then open Revenue, Retention, Delivery, Reconciliation and Operations pages.
8. Put the actual working web URL in the README and portfolio only after verifying that it serves real historical Olist data.

## Credentials

- Store runtime values in Railway's private service variables (not GitHub).
- The database `DATABASE_URL` and `PG*` references belong to the loader. The dashboard has its own limited user credentials.
- Never copy database tokens or passwords into README, Actions logs, screenshots or public issues.
- Public Olist data has attribution and noncommercial-sharealike license requirements. Cite the original Kaggle source in the app and any derived reports.

## Technical warnings

- A public dashboard without a loaded persistent database will be visible but not functional.
- The loader's early validations do not establish the authenticity of the downloaded files; they verify contracts, identifiers and size.
- Some public datasets have review references or other anomalies; the profiler reports these as warnings rather than asserting they are fraud or financial discrepancies.
- Once your app is deployed, review Railway's service billing and backup settings periodically.

For general Railway instructions, see https://docs.railway.com/services and https://docs.railway.com/databases/postgresql.

**Do not use a legacy `railway.json` or `railway.toml` on a new deployment.** Railway's config-as-code was deprecated in favor of its newer Infrastructure as Code mechanism in late 2026; configure the two service Dockerfiles through the provider settings or its current agent integration.

## Railway free-plan storage and sampling

The current Railway plan allows only a **500 MB PostgreSQL volume**. Importing all original Olist source rows exceeded that limit. The private loader supports `COMMERCEIQ_SAMPLE_PERCENT=5`, which hashes `customer_unique_id` to select approximately 5% of real historical customers and retains all their related orders, items, payments and reviews. Geographic source records are reduced to one observation per relevant postal prefix because geography is not used by the dashboard marts. **This is not the full dataset** and its statistics must not be described as population-wide estimates.

For this initial deployment only, set `COMMERCEIQ_RESET_FROM_FAILED_FULL_LOAD=true` on the private loader to clear the incomplete earlier raw import before loading the bounded sample. Once the sample finishes, **change that variable to `false`** so a later retry cannot delete the populated warehouse. Do not reset unrelated databases.

Keep the public dashboard's `DATABASE_URL` pointed to the least-privilege `commerceiq_dashboard` login, never the PostgreSQL owner account. The loader provisions this reader role after its warehouse audit passes, using `COMMERCEIQ_DASHBOARD_PASSWORD` supplied through Railway variables. The public service uses the role's credentials via Railway environment-variable references.
