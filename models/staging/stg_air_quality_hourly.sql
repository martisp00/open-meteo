-- Staging: hourly air quality, one row per city per hour.
-- The raw column "timestamp" is a SQL keyword, so we quote it and rename to datetime.
with source as (
    select * from {{ source('raw', 'raw_air_quality_hourly') }}
)

select
    city_name,
    country_code,
    cast("timestamp" as timestamp)   as datetime,
    cast(pm10 as double)             as pm10,
    cast(pm2_5 as double)            as pm2_5,
    cast(carbon_monoxide as double)  as carbon_monoxide,
    cast(nitrogen_dioxide as double) as nitrogen_dioxide,
    cast(ozone as double)            as ozone,
    cast(european_aqi as double)     as european_aqi
from source
