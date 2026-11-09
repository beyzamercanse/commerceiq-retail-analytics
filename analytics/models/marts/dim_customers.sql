-- One row per stable customer identity, not Olist's order-specific customer_id.
with ranked as (
    select
        customer_unique_id,
        customer_city,
        customer_state,
        zip_code_prefix,
        row_number() over (
            partition by customer_unique_id order by customer_id desc
        ) as row_rank
    from {{ ref('stg_customers') }}
    where customer_unique_id is not null
)
select
    customer_unique_id,
    customer_city,
    customer_state,
    zip_code_prefix
from ranked
where row_rank = 1

