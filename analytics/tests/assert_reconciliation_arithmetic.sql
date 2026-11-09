select order_id
from {{ ref('fct_orders') }}
where abs(
    reconciliation_difference_brl - (recorded_payment_brl - expected_payment_brl)
) > 0.01

