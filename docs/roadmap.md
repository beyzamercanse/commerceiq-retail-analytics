# CommerceIQ milestone roadmap

- [x] Phase 1 — Nine CSV contracts, PostgreSQL ingestion and tests.
- [x] Phase 2 — dbt staging, dimensional facts, marts and SQL tests.
- [x] Phase 3 — Streamlit dashboards, audited refresh, reporting smoke tests.
- [x] Phase 4A — Warehouse audit CLI, read-only database role and deployment documentation.
- [x] Phase 4B code — Full-data CSV profiler, Docker web/loader images, Railway deployment playbook and container CI builds.
- [ ] Phase 4B hosting — Connect Railway, provision private PostgreSQL, load and audit original Olist, configure limited user and publish working public web URL.
- [ ] Optional later — Scale benchmarks, lineage and handling changing source feeds.

**CI validates synthetic inputs; it is not evidence of a live website or full original dataset ingestion.**

See [Railway deployment](railway-deployment.md), [Operations](operations.md), and [Demo](demo_script.md).
