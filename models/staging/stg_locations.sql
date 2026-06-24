-- Staging: city metadata and coordinates. One row per city.
-- Rename for clarity, cast numerics, drop extraction metadata.
with source as (
    select * from {{ source('raw', 'raw_locations') }}
)

select
    location_id,
    city_name,
    country,
    country_code,
    admin1 as region,
    cast(latitude as double)  as latitude,
    cast(longitude as double) as longitude,
    timezone,
    cast(elevation as double) as elevation,
    cast(population as bigint) as population
from source
