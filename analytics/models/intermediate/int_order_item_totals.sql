select
    order_id,
    count(*) as item_count,
    sum(price_brl) as item_subtotal_brl,
    sum(freight_value_brl) as freight_total_brl,
    sum(price_brl + freight_value_brl) as item_and_freight_total_brl
from {{ ref('stg_order_items') }}
group by order_id

