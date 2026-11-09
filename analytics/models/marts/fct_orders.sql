-- Grain: exactly one row per order. Both multivalued children are pre-aggregated.
select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.purchased_at,
    o.purchased_at::date as purchase_date,
    o.approved_at,
    o.delivered_to_carrier_at,
    o.delivered_to_customer_at,
    o.estimated_delivery_at,
    (o.delivered_to_customer_at > o.estimated_delivery_at) as is_late_delivery,
    coalesce(i.item_count, 0) as item_count,
    coalesce(i.item_subtotal_brl, 0::numeric) as item_subtotal_brl,
    coalesce(i.freight_total_brl, 0::numeric) as freight_total_brl,
    coalesce(i.item_and_freight_total_brl, 0::numeric) as expected_payment_brl,
    coalesce(p.payment_count, 0) as payment_count,
    coalesce(p.payment_total_brl, 0::numeric) as recorded_payment_brl,
    coalesce(p.payment_total_brl, 0::numeric)
        - coalesce(i.item_and_freight_total_brl, 0::numeric) as reconciliation_difference_brl,
    coalesce(r.review_count, 0) as review_count,
    r.average_review_score
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c on o.customer_id = c.customer_id
left join {{ ref('int_order_item_totals') }} i on o.order_id = i.order_id
left join {{ ref('int_order_payment_totals') }} p on o.order_id = p.order_id
left join {{ ref('int_order_review_summary') }} r on o.order_id = r.order_id

