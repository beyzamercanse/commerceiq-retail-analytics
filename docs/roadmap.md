# CommerceIQ implementation roadmap

- [x] Phase 1 — Python CSV contracts, idempotent PostgreSQL ingestion, CI tests.
- [x] Phase 2 — dbt staging, intermediate aggregates, dimensional facts, revenue/retention/delivery/reconciliation marts.
- [x] Phase 3 — Streamlit dashboards, audited refresh command, source and run monitoring, SQL reporting tests and CI smoke checks.
- [ ] Phase 4 (optional) — Real historical Olist data validation, read-only DB roles, persistent hosted PostgreSQL, deployed dashboards, scheduled orchestration and alerting.

**Phase 3 is a runnable local application, not an externally hosted live BI service.** All reported result samples in CI use synthetic datasets, and CI must pass before this milestone is considered verified.

Documentation: [Operations](operations.md), [Architecture](architecture.md), [Data Contracts](data-contracts.md), [dbt models](../analytics/README.md).
