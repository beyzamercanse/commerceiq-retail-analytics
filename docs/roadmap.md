# CommerceIQ milestone roadmap

- [x] Phase 1 — Nine CSV contracts, PostgreSQL ingestion and tests.
- [x] Phase 2 — dbt staging, dimensional facts, marts and SQL tests.
- [x] Phase 3 — Streamlit dashboards, audited refresh, reporting smoke tests.
- [x] Phase 4A — Warehouse audit CLI, read-only database role and deployment documentation.
- [x] Phase 4B code — Full-data CSV profiler, Docker web/loader images, Railway deployment playbook and container CI builds.
- [x] Phase 4B hosting — Railway PostgreSQL and Streamlit service deployed, deterministic historical 5% sample loaded (5,081 orders), dbt tests passed, restricted reader login configured, Railway-managed public domain assigned.
- [ ] Optional later — Scale benchmarks, lineage and handling changing source feeds.

**Production serves sampled historical data, not the full Olist dataset.** Railway reports successful service deployments; an independent external HTTP fetch of the published domain was not possible from this environment. CI continues to validate the synthetic fixtures separately.

See [Railway deployment](railway-deployment.md), [Operations](operations.md), and [Demo](demo_script.md).
