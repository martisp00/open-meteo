-- Singular test: a day's minimum temperature should never exceed its maximum.
-- Returns rows only when violated, so any result means the test fails.
select
    city_name,
    date,
    temperature_2m_min,
    temperature_2m_max
from {{ ref('fct_city_weather_day') }}
where temperature_2m_min > temperature_2m_max
