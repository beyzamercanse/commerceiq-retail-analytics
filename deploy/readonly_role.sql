-- Execute as the database owner / a privileged administrator AFTER dbt build.
-- The group role has NOLOGIN; create an independent login in your cloud DB
-- and GRANT commerceiq_dashboard_reader TO that login with an administrator.
-- Never put a credential in this SQL file.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'commerceiq_dashboard_reader') THEN
        CREATE ROLE commerceiq_dashboard_reader NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA analytics_marts, raw, ops TO commerceiq_dashboard_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics_marts TO commerceiq_dashboard_reader;
GRANT SELECT ON raw.source_files TO commerceiq_dashboard_reader;
GRANT SELECT ON ops.pipeline_runs TO commerceiq_dashboard_reader;

-- Run default privileges as the role that creates/replaces dbt marts.
-- For a different table-owner role, use ALTER DEFAULT PRIVILEGES FOR ROLE ... .
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics_marts
    GRANT SELECT ON TABLES TO commerceiq_dashboard_reader;

-- Grant permissions to newly created logs/manifest tables if replaced by the owner.
ALTER DEFAULT PRIVILEGES IN SCHEMA ops
    GRANT SELECT ON TABLES TO commerceiq_dashboard_reader;

-- Keep raw tables (customer and order-level data) inaccessible to the dashboard.
