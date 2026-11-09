-- Keep all orders including unpaid, canceled, incomplete, and potentially revised records.
-- Differences are evidence for investigation, NOT automatically errors.
select
    order_id,
    purchase_date,
    order_status,
    item_count,
    payment_count,
    expected_payment_brl,
    recorded_payment_brl,
    reconciliation_difference_brl,
    case
        when item_count = 0 and payment_count = 0 then 'no_items_or_payments'
        when item_count = 0 then 'payment_without_items'
        when payment_count = 0 then 'items_without_payments'
        when abs(reconciliation_difference_brl) <= 0.01 then 'balanced'
        else 'investigate'
    end as reconciliation_status
from {{ ref('fct_orders') }}

