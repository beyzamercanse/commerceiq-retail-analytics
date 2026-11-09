-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (product_category_name)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'category_translation') }}
)
select
    nullif(btrim(product_category_name), '') as product_category_name,
    nullif(btrim(product_category_name_english), '') as category_name_english
from ranked
where _version_rank = 1

