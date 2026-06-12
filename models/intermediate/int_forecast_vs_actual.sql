-- Join forecast to actuals on city + date for accuracy comparison
select
    f.city_name,
    f.date,
    f.temperature_2m_max                              as forecast_temp_max,
    w.temperature_2m_max                              as actual_temp_max,
    f.temperature_2m_max - w.temperature_2m_max       as temp_error
from {{ ref('stg_forecast_daily') }} f
left join {{ ref('stg_weather_daily') }} w
    on f.city_name = w.city_name
    and f.date = w.date
