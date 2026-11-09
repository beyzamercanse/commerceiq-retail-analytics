select order_id, payment_sequential
from {{ ref('fct_payments') }}
group by order_id, payment_sequential
having count(*) > 1

