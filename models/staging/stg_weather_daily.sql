select * from {{ source('raw', 'raw_weather_daily') }}
