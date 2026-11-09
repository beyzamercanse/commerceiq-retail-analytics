-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (order_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'orders') }}
)
select
    nullif(btrim(order_id), '') as order_id,
    nullif(btrim(customer_id), '') as customer_id,
    nullif(btrim(order_status), '') as order_status,
    nullif(order_purchase_timestamp, '')::timestamp as purchased_at,
    nullif(order_approved_at, '')::timestamp as approved_at,
    nullif(order_delivered_carrier_date, '')::timestamp as delivered_to_carrier_at,
    nullif(order_delivered_customer_date, '')::timestamp as delivered_to_customer_at,
    nullif(order_estimated_delivery_date, '')::timestamp as estimated_delivery_at
from ranked
where _version_rank = 1

