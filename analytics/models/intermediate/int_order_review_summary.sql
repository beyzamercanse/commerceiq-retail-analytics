select
    order_id,
    count(*) as review_count,
    avg(review_score::numeric) as average_review_score
from {{ ref('stg_reviews') }}
group by order_id

