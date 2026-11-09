# CommerceIQ operating runbook

## Local repeatable refresh

From the repository root:

```bash
cp .env.example .env
python -m pip install -e '.[dev,dashboard]' 'dbt-postgres>=1.9,<2'
docker compose up -d --wait
export DBT_PROFILES_DIR=analytics
commerceiq-refresh --data-dir data/sample_olist
commerceiq-audit --min-orders 3 --out artifacts/quality_audit.json
streamlit run dashboard/app.py
```

The audited refresh first reads the source CSVs, skips unchanged file hashes, builds and tests dbt, then records success or failure in `ops.pipeline_runs`. A failed dbt build does not roll back previously ingested raw batches; retrying the same files is safe.

`commerceiq-audit` independently checks source manifest coverage, order and line-level grain, and dated daily-mart totals. It emits aggregate-only JSON and exits nonzero on a violation. **This proves consistency with the loaded source, not the authenticity of an external dataset or accounting revenue.**

CI runs with a disposable PostgreSQL service, creates the mart tables from synthetic fixtures, checks the audit and reader-role permissions, and uploads the JSON audit as a job artifact.

## Failure and recovery

| Problem | Action |
|---|---|
| Missing CSV | Inspect source folder and filenames |
| Unexpected CSV columns | Check exact Olist header; ingestion is transactional per file |
| PostgreSQL unavailable | Start Docker Compose and verify connection settings |
| dbt model/test fails | Inspect dbt logs, correct source/model, repeat audited refresh |
| Audit fails | Compare the violated grain/metric count with staged and fact records |
| Streamlit cannot connect | Verify TLS/network, read-only URL, and `DBT_SCHEMA` |
| CI failure | Inspect the failed job and uploaded audit artifact, if generated |

## Data limitations

- Fixture CSVs are synthetic; Olist records are historical (2016–2018).
- Brazilian-real merchandise values exclude accounting adjustments and are not recognized revenue.
- Cohorts near dataset end are right-censored.
- An anomalous payment difference is an investigation candidate, not confirmed leakage.
- Last-loaded timestamps record CommerceIQ ingestion time, not source-system freshness.
- Ingestion is append-only by file hash, not a full change-data-capture system.

## Production caveats

There is **no public hosted app or managed database configured by the repository**. See [deployment steps](deployment.md). Hosted environments require backups, credentials segregation, careful data access controls and provider billing review. Olist is a static historical dataset, so automatic daily refresh is not meaningful without new data.
