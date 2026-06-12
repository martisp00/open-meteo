select
    city_name,
    latitude,
    longitude,
    country_code,
    timezone
from {{ ref('stg_locations') }}
