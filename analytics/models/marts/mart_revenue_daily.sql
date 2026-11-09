-- GMV-like order item subtotal, NOT recognized revenue or profit.
select
    purchase_date,
    count(*) as order_count,
    count(*) filter (where order_status = 'delivered') as delivered_order_count,
    sum(item_count) as items_sold,
    sum(item_subtotal_brl) as gross_item_value_brl,
    sum(freight_total_brl) as freight_value_brl,
    sum(recorded_payment_brl) as recorded_payment_brl,
    sum(item_subtotal_brl) / nullif(count(*), 0) as average_order_item_value_brl
from {{ ref('fct_orders') }}
where purchase_date is not null
group by purchase_date

