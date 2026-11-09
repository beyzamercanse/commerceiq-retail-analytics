-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (review_id), (order_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'reviews') }}
)
select
    nullif(btrim(review_id), '') as review_id,
    nullif(btrim(order_id), '') as order_id,
    nullif(review_score, '')::integer as review_score,
    nullif(btrim(review_comment_title), '') as review_title,
    nullif(btrim(review_comment_message), '') as review_comment,
    nullif(review_creation_date, '')::timestamp as review_created_at,
    nullif(review_answer_timestamp, '')::timestamp as review_answered_at
from ranked
where _version_rank = 1

