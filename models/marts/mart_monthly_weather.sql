-- Mart: one row per city per month with aggregated weather metrics.
select
    city_name,
    date_trunc('month', date)                                              as month,
    count(*)                                                               as days_observed,
    round(avg(temperature_2m_mean), 1)                                     as avg_temp,
    round(min(temperature_2m_min), 1)                                      as min_temp,
    round(max(temperature_2m_max), 1)                                      as max_temp,
    round(sum(precipitation_sum), 1)                                       as total_precipitation,
    round(avg(wind_speed_10m_max), 1)                                      as avg_wind_speed,
    sum(case when is_heat_day then 1 else 0 end)                           as heat_days,
    sum(case when is_freezing_day then 1 else 0 end)                       as freezing_days,
    sum(case when is_heavy_rain_day then 1 else 0 end)                     as heavy_rain_days,
    sum(case when is_comfortable_day then 1 else 0 end)                    as comfortable_days
from {{ ref('fct_city_weather_day') }}
group by 1, 2
