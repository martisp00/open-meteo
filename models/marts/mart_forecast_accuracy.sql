-- Mart: forecast accuracy summary per city (mean absolute temperature error).
select
    city_name,
    count(*)                       as days_compared,
    round(avg(abs(temp_error)), 2) as mae_temp,
    round(max(abs(temp_error)), 2) as max_temp_error
from {{ ref('int_forecast_vs_actual') }}
group by 1
