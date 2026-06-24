-- Fact: one row per city per day, weather metrics plus daily air quality.
-- Air quality only exists for the forecast horizon, so older days have null AQ.
select
    w.city_name,
    w.date,
    w.temperature_2m_max,
    w.temperature_2m_min,
    w.temperature_2m_mean,
    w.precipitation_sum,
    w.wind_speed_10m_max,
    w.is_heat_day,
    w.is_freezing_day,
    w.is_heavy_rain_day,
    w.is_windy_day,
    w.is_comfortable_day,
    aq.avg_pm2_5,
    aq.avg_pm10,
    aq.avg_aqi
from {{ ref('int_weather_flags') }} w
left join {{ ref('int_air_quality_daily') }} aq
    on w.city_name = aq.city_name
   and w.date = aq.date
