select
    order_id,
    count(*) as payment_count,
    sum(payment_value_brl) as payment_total_brl
from {{ ref('stg_payments') }}
group by order_id

