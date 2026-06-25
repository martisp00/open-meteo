-- Mart: one row per city summarizing weather risk over the period.
-- risk_score = percent of days that were a heat day, heavy-rain day, OR windy day.
select
    city_name,
    count(*)                                                  as days_observed,
    sum(case when is_heat_day then 1 else 0 end)              as heat_days,
    sum(case when is_heavy_rain_day then 1 else 0 end)        as heavy_rain_days,
    sum(case when is_windy_day then 1 else 0 end)             as windy_days,
    round(
        100.0 * sum(case when is_heat_day or is_heavy_rain_day or is_windy_day then 1 else 0 end) / count(*),
        1
    )                                                         as risk_score
from {{ ref('fct_city_weather_day') }}
group by 1
