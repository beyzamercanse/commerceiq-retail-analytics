-- Cohort month: first purchase; repeat order logic based on stable customer_unique_id.
with purchases as (
    select
        customer_unique_id,
        order_id,
        purchased_at,
        date_trunc('month', purchased_at)::date as order_month
    from {{ ref('fct_orders') }}
    where customer_unique_id is not null
      and purchased_at is not null
      and order_status not in ('canceled', 'unavailable')
),
first_purchase as (
    select customer_unique_id, min(order_month) as cohort_month
    from purchases
    group by customer_unique_id
),
cohort_activity as (
    select distinct
        p.customer_unique_id,
        fp.cohort_month,
        p.order_month,
        (
            (extract(year from p.order_month)::integer - extract(year from fp.cohort_month)::integer) * 12
            + (extract(month from p.order_month)::integer - extract(month from fp.cohort_month)::integer)
        ) as months_since_first_purchase
    from purchases p
    inner join first_purchase fp on p.customer_unique_id = fp.customer_unique_id
)
select
    cohort_month,
    months_since_first_purchase,
    count(distinct customer_unique_id) as active_customers
from cohort_activity
group by cohort_month, months_since_first_purchase

