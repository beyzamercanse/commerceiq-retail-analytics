# CommerceIQ warehouse architecture

\`\`\`mermaid
flowchart TB
    A[Olist source CSVs] --> B[Python source validation and batch ingestion]
    B --> C[(PostgreSQL raw schema)]
    B --> D[Source hash, load timestamp, batch manifest]
    C --> E[dbt staging - 9 models]
    E --> F[dbt intermediate order aggregations]
    E --> G[dbt customer, seller and product dimensions]
    E --> H[dbt line facts - items and payments]
    F --> I[dbt order fact]
    G --> I
    I --> J[Revenue, retention, delivery and reconciliation marts]
    H --> K[dbt reconciliation tests]
    I --> K
    J --> L[Business intelligence - Phase 3]
\`\`\`

**Raw** text columns preserve original input values and lineage. **Staging** applies type conversions and deduplication by business key. **Intermediate** groups multivalued item and payment sources before joining to the **order grain**. **Marts** expose curated analytical tables.

CI tests source ingestion with PostgreSQL and then builds the dbt project. Historical reprocessing uses the existing source-file SHA-256 idempotency mechanism.

