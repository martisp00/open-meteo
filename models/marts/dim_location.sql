-- Dimension: one row per city with descriptive attributes.
select
    location_id,
    city_name,
    country,
    country_code,
    region,
    latitude,
    longitude,
    timezone,
    elevation,
    population
from {{ ref('stg_locations') }}
