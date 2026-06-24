-- Mart: one row per city summarizing comfort and risk over the whole period.
-- Powers the dashboard city ranking. comfort_score = percent of comfortable days.
select
    f.city_name,
    d.country,
    count(*)                                                             as days_observed,
    round(avg(f.temperature_2m_mean), 1)                                as avg_temp,
    round(avg(f.precipitation_sum), 1)                                  as avg_precipitation,
    sum(case when f.is_comfortable_day then 1 else 0 end)               as comfortable_days,
    sum(case when f.is_heat_day then 1 else 0 end)                      as heat_days,
    sum(case when f.is_heavy_rain_day then 1 else 0 end)                as rainy_days,
    sum(case when f.is_windy_day then 1 else 0 end)                     as windy_days,
    round(100.0 * sum(case when f.is_comfortable_day then 1 else 0 end) / count(*), 1) as comfort_score
from {{ ref('fct_city_weather_day') }} f
left join {{ ref('dim_location') }} d
    on f.city_name = d.city_name
group by 1, 2
