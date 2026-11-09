-- A postal code occurs many times in Olist geolocation, so do not join raw rows to orders.
-- Representative coordinates are averages, NOT official postal centroids.
select
    nullif(btrim(geolocation_zip_code_prefix), '') as zip_code_prefix,
    avg(nullif(geolocation_lat, '')::double precision) as mean_latitude,
    avg(nullif(geolocation_lng, '')::double precision) as mean_longitude,
    count(*) as source_observation_count
from {{ source('olist_raw', 'geolocation') }}
where nullif(btrim(geolocation_zip_code_prefix), '') is not null
group by 1

