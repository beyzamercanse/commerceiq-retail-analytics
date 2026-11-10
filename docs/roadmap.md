# CommerceIQ milestone roadmap

- [x] Phase 1 — Nine CSV contracts, PostgreSQL ingestion and tests.
- [x] Phase 2 — dbt staging, dimensional facts, marts and SQL tests.
- [x] Phase 3 — Streamlit dashboards, audited refresh, reporting smoke tests.
- [x] Phase 4A — Warehouse audit CLI, read-only database role and deployment documentation.
- [x] Phase 4B code — Full-data CSV profiler, Docker web/loader images, Railway deployment playbook and container CI builds.
- [ ] Phase 4B hosting — Railway project and private PostgreSQL are provisioned; finish loading and auditing a real historical 5% customer sample, configure the restricted dashboard login and validate the public URL.
- [ ] Optional later — Scale benchmarks, lineage and handling changing source feeds.

**CI validates synthetic inputs; it is not evidence of a live website or full original dataset ingestion.**

See [Railway deployment](railway-deployment.md), [Operations](operations.md), and [Demo](demo_script.md).
