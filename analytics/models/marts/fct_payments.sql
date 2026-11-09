-- Grain: one payment sequence per order.
select
    p.order_id,
    p.payment_sequential,
    p.payment_type,
    p.payment_installments,
    p.payment_value_brl
from {{ ref('stg_payments') }} p

