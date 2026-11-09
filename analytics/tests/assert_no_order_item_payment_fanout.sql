-- Every order's aggregated item count must match the original item-level fact count.
with actual as (
    select order_id, count(*) as n
    from {{ ref('fct_order_items') }}
    group by order_id
)
select o.order_id, o.item_count, coalesce(a.n, 0) as fact_item_count
from {{ ref('fct_orders') }} o
left join actual a on o.order_id = a.order_id
where o.item_count <> coalesce(a.n, 0)

