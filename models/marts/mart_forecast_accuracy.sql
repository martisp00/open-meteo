select
    city_name,
    count(*)                   as days_compared,
    avg(abs(temp_error))       as mae_temp,
    max(abs(temp_error))       as max_temp_error
from {{ ref('int_forecast_vs_actual') }}
where actual_temp_max is not null
group by 1
