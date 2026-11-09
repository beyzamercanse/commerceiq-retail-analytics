with actual as (
    select order_id, sum(payment_value_brl) as amount
    from {{ ref('fct_payments') }}
    group by order_id
)
select o.order_id
from {{ ref('fct_orders') }} o
left join actual a on o.order_id = a.order_id
where abs(o.recorded_payment_brl - coalesce(a.amount, 0)) > 0.01

