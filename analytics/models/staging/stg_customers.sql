-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (customer_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'customers') }}
)
select
    nullif(btrim(customer_id), '') as customer_id,
    nullif(btrim(customer_unique_id), '') as customer_unique_id,
    nullif(btrim(customer_zip_code_prefix), '') as zip_code_prefix,
    nullif(btrim(customer_city), '') as customer_city,
    nullif(btrim(customer_state), '') as customer_state
from ranked
where _version_rank = 1

