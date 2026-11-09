select
    purchase_date,
    count(*) filter (where delivered_to_customer_at is not null) as delivered_count,
    count(*) filter (where is_late_delivery is true) as late_delivery_count,
    round(
        (count(*) filter (where is_late_delivery is true))::numeric
        / nullif(count(*) filter (where delivered_to_customer_at is not null), 0),
        4
    ) as late_delivery_rate
from {{ ref('fct_orders') }}
where purchase_date is not null
group by purchase_date

