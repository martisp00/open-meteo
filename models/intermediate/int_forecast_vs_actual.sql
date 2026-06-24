-- Join forecast to actuals on city + date to measure forecast error.
-- Inner join keeps only dates where both a forecast and an actual exist.
select
    f.city_name,
    f.date,
    f.temperature_2m_max                        as forecast_temp_max,
    a.temperature_2m_max                        as actual_temp_max,
    f.temperature_2m_max - a.temperature_2m_max as temp_error
from {{ ref('stg_forecast_daily') }} f
inner join {{ ref('stg_weather_daily') }} a
    on f.city_name = a.city_name
   and f.date = a.date
