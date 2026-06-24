-- Aggregate hourly air quality to one row per city per day.
select
    city_name,
    cast(datetime as date) as date,
    avg(pm2_5)        as avg_pm2_5,
    avg(pm10)         as avg_pm10,
    max(pm2_5)        as max_pm2_5,
    avg(european_aqi) as avg_aqi
from {{ ref('stg_air_quality_hourly') }}
group by 1, 2
