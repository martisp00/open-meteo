select
    w.city_name,
    w.date,
    w.temperature_2m_max,
    w.temperature_2m_min,
    w.precipitation_sum,
    w.is_heat_day,
    w.is_heavy_rain_day,
    aq.avg_pm2_5,
    aq.avg_pm10
from {{ ref('int_weather_flags') }} w
left join {{ ref('int_air_quality_daily') }} aq
    on w.city_name = aq.city_name
    and w.date = aq.date
