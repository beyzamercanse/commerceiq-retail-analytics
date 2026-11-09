-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (seller_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'sellers') }}
)
select
    nullif(btrim(seller_id), '') as seller_id,
    nullif(btrim(seller_zip_code_prefix), '') as zip_code_prefix,
    nullif(btrim(seller_city), '') as seller_city,
    nullif(btrim(seller_state), '') as seller_state
from ranked
where _version_rank = 1

