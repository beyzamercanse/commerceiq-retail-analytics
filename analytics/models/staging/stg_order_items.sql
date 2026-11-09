-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (order_id), (order_item_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'order_items') }}
)
select
    nullif(btrim(order_id), '') as order_id,
    nullif(order_item_id, '')::integer as order_item_id,
    nullif(btrim(product_id), '') as product_id,
    nullif(btrim(seller_id), '') as seller_id,
    nullif(shipping_limit_date, '')::timestamp as shipping_limit_at,
    nullif(price, '')::numeric(18,2) as price_brl,
    nullif(freight_value, '')::numeric(18,2) as freight_value_brl
from ranked
where _version_rank = 1

