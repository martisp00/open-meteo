select * from {{ source('raw', 'raw_forecast_daily') }}
