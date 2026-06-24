-- Enrich daily weather with simple comfort and risk flags.
-- One row per city per day, same grain as staging.
select
    city_name,
    country_code,
    date,
    temperature_2m_max,
    temperature_2m_min,
    temperature_2m_mean,
    precipitation_sum,
    wind_speed_10m_max,

    -- risk flags
    case when temperature_2m_max >= 35 then true else false end as is_heat_day,
    case when temperature_2m_min <= 0  then true else false end as is_freezing_day,
    case when precipitation_sum >= 20  then true else false end as is_heavy_rain_day,
    case when wind_speed_10m_max >= 40 then true else false end as is_windy_day,

    -- a day is "comfortable" if it is mild, dry, and calm
    case
        when temperature_2m_mean between 18 and 26
         and precipitation_sum < 1
         and wind_speed_10m_max < 25
        then true else false
    end as is_comfortable_day
from {{ ref('stg_weather_daily') }}
