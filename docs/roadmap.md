# CommerceIQ implementation roadmap

- [x] Phase 1 — Nine CSV source contracts, idempotent PostgreSQL ingestion, CI.
- [x] Phase 2 — dbt staging, dimensional facts and business marts.
- [x] Phase 3 — Streamlit dashboards, audited refresh, reporting tests.
- [x] Phase 4A — Warehouse audit CLI, aggregate quality evidence in CI, least-privilege dashboard reader design, deployment instructions and interview demo.
- [ ] Phase 4B — Load and verify the original full Olist dataset, provision persistent hosted PostgreSQL, grant read-only credentials and publish the actual hosted Streamlit app.
- [ ] Optional — Scheduled ingestion and operational alerts when a changing data source is introduced.

**Phase 4A adds deployment-ready code, not a deployed cloud service.** CI uses disposable PostgreSQL and synthetic fixtures.

See [Deployment](deployment.md), [Operations](operations.md), [Demo](demo_script.md), and [Architecture](architecture.md).
