# Architecture

```mermaid
flowchart TB
  A[Olist CSV source] --> B[Python typed CSV/header validation]
  B --> C[PostgreSQL raw.*]
  B --> D[SHA-256 file manifest]
  C --> E[dbt staging - Phase 2]
  D --> E
  E --> F[Dimensional marts - Phase 2]
  F --> G[Dashboards - Phase 3]
```

Raw columns retain original text values. Each file is copied in a database transaction with an audit manifest. Same-content reruns are skipped based on SHA-256. This is an append-only raw store: effective-version merging is future work.

Do not directly join order items and payments: both have multiple records per order and create a fanout. In the next milestone, aggregate to compatible grains or use separate fact tables.