-- Mart: one row per city summarizing air quality over the days where it exists.
-- Air quality only covers the forecast horizon, so this reflects a few recent days.
select
    city_name,
    count(*)                       as days_with_air_quality,
    round(avg(avg_pm2_5), 1)       as avg_pm2_5,
    round(avg(avg_pm10), 1)        as avg_pm10,
    round(avg(avg_aqi), 1)         as avg_aqi,
    case
        when avg(avg_aqi) <= 20 then 'Good'
        when avg(avg_aqi) <= 40 then 'Fair'
        when avg(avg_aqi) <= 60 then 'Moderate'
        else 'Poor'
    end                            as aqi_category
from {{ ref('int_air_quality_daily') }}
group by 1
