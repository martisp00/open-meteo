select * from {{ source('raw', 'raw_air_quality_hourly') }}
