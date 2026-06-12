-- Add derived flags to daily weather
select
    *,
    case when temperature_2m_max > 35 then true else false end as is_heat_day,
    case when precipitation_sum > 20 then true else false end  as is_heavy_rain_day
from {{ ref('stg_weather_daily') }}
