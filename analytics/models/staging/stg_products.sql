-- Source records can be re-ingested in multiple batches; prefer latest batch per business key.
with ranked as (
    select
        *,
        row_number() over (
            partition by (product_id)
            order by _loaded_at desc, _source_sha256 desc, _row_number desc
        ) as _version_rank
    from {{ source('olist_raw', 'products') }}
)
select
    nullif(btrim(product_id), '') as product_id,
    nullif(btrim(product_category_name), '') as product_category_name,
    nullif(product_name_lenght, '')::integer as product_name_length,
    nullif(product_description_lenght, '')::integer as product_description_length,
    nullif(product_photos_qty, '')::integer as product_photos_qty,
    nullif(product_weight_g, '')::numeric as product_weight_g,
    nullif(product_length_cm, '')::numeric as product_length_cm,
    nullif(product_height_cm, '')::numeric as product_height_cm,
    nullif(product_width_cm, '')::numeric as product_width_cm
from ranked
where _version_rank = 1

