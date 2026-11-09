-- Grain: one item sequence per order. DO NOT join directly to payment lines.
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.purchased_at::date as purchase_date,
    i.shipping_limit_at,
    i.price_brl,
    i.freight_value_brl,
    (i.price_brl + i.freight_value_brl) as item_and_freight_brl
from {{ ref('stg_order_items') }} i
left join {{ ref('stg_orders') }} o on i.order_id = o.order_id

