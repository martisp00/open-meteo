# Modeling Choices

Document the key decisions made during the project here.

## Granularity

- `fct_city_weather_day`: one row per **city × day**
- Air quality is aggregated from hourly → daily in `int_air_quality_daily`

## Materialization

| Layer | Strategy | Reason |
|-------|----------|--------|
| Staging | View | Raw pass-through, no transformation cost |
| Intermediate | View | Consumed only by marts |
| Marts | Table | Dashboard reads these repeatedly |

## Tests

- `unique` + `not_null` on all primary keys
- Relationship tests between facts and dimensions

## Known Limitations

- 
