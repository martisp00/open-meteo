-- Staging: daily weather forecast, one row per city per day.
with source as (
    select * from {{ source('raw', 'raw_forecast_daily') }}
)

select
    city_name,
    country_code,
    cast(date as date)                  as date,
    cast(temperature_2m_max as double)  as temperature_2m_max,
    cast(temperature_2m_min as double)  as temperature_2m_min,
    cast(temperature_2m_mean as double) as temperature_2m_mean,
    cast(precipitation_sum as double)   as precipitation_sum,
    cast(rain_sum as double)            as rain_sum,
    cast(snowfall_sum as double)        as snowfall_sum,
    cast(wind_speed_10m_max as double)  as wind_speed_10m_max
from source
