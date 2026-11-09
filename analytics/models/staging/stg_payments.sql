-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (order_id), (payment_sequential)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'payments') }}
)
select
    nullif(btrim(order_id), '') as order_id,
    nullif(payment_sequential, '')::integer as payment_sequential,
    nullif(btrim(payment_type), '') as payment_type,
    nullif(payment_installments, '')::integer as payment_installments,
    nullif(payment_value, '')::numeric(18,2) as payment_value_brl
from ranked
where _version_rank = 1

