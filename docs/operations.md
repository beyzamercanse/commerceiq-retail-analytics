# CommerceIQ operating runbook

## Local repeatable refresh

From the repository root:

\`\`\`bash
cp .env.example .env
python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2'
docker compose up -d --wait
export DBT_PROFILES_DIR=analytics
commerceiq-refresh --data-dir data/sample_olist
streamlit run dashboard/app.py
\`\`\`

On Windows PowerShell, activate your environment and use \`$env:DBT_PROFILES_DIR="analytics"\`.
If you change the PostgreSQL password in \`.env\`, also set \`DBT_PASSWORD\`.

### Responsibilities

1. \`commerceiq-refresh\` starts an audited run in \`ops.pipeline_runs\`.
2. Python validates each CSV and records immutable source files by SHA-256.
3. dbt builds staging/intermediate/marts and executes data-quality tests.
4. The audit row records success or failure, batch counters, and completion timestamp.
5. The Streamlit Operations page displays ingestion timestamps and audited runs.

The job is repeatable: unchanged raw input is skipped, while dbt still refreshes the derived warehouse.
A failed dbt build does **not** roll back prior successful raw ingestion. Running again is safe for identical file content.

## Reporting verification

\`\`\`bash
pytest
pytest -o addopts= -m reporting
dbt docs generate --project-dir analytics --profiles-dir analytics
\`\`\`

GitHub Actions creates a disposable PostgreSQL service, ingests synthetic fixtures, builds dbt, runs an audited refresh, and checks SQL-based reporting results and the dashboard's revenue view. This **does not** deploy a hosted app.

## Dataset and metric caveats

- The bundled nine CSV files are **synthetic smoke-test inputs**. Load the real historical Olist CSVs into \`data/olist/\` before interpreting metrics.
- Source records cover historical 2016–2018 commerce activity, **not** a current or streaming market.
- BRL item values are merchandise amounts, not profit or recognized revenue.
- Split payments, canceled orders and missing items affect reconciliation; a discrepancy is an investigation candidate.
- Monthly cohorts are right-censored near the dataset end. No causal inference is implied.
- Ingestion "last loaded" timestamps mean *our load time*, not source-event freshness or contractual SLA.
- Raw storage is append-only by file hash; later source batches supersede business records in staging based on load order. This is not true CDC history.

## Failure and recovery

| Situation | Response |
|---|---|
| Missing CSV/header mismatch | Fix source file or use \`--allow-partial\` to intentionally accept a subset |
| PostgreSQL unavailable | Start Docker, verify credentials and run \`commerceiq status\` |
| dbt build fails | Inspect dbt logs, repair source/model, rerun \`commerceiq-refresh\` |
| Reports show old data | Verify latest \`ops.pipeline_runs\` status and rerun warehouse build |
| Dashboard connection failure | Check \`DATABASE_URL\`, \`DBT_SCHEMA\`, PostgreSQL and the mart tables |
| Automated cloud refresh requested | Provision a persistent DB and scheduler first; GitHub CI's DB is disposable |

No hosted database, hosted dashboard, scheduler, customer alerting or SLA is configured in this phase.

## Recommended enhancements

Set a documented source-freshness target only after moving beyond static Olist files. For production-like deployment, configure secret-managed hosted PostgreSQL, persistent scheduling, retries and alerts, read-only dashboard credentials, and monitoring of expected daily partitions.
