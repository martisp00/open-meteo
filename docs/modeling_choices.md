# Modeling choices

Some notes on why we built the project the way we did, not just what it does.

## Layers

We used the standard staging / intermediate / marts split from class.

- **Staging** just cleans each raw table: rename columns to clear names, cast types,
  and drop the extraction metadata we don't need. One staging model per source, no joins.
- **Intermediate** is where the actual logic happens: aggregating air quality from hourly
  to daily, adding weather flags, and joining the forecast to the actuals.
- **Marts** are the final tables the dashboard reads.

Keeping joins out of staging was deliberate. Staging stays a simple one-source-in,
one-model-out layer so it is easy to reason about, and all the joining happens later.

## The timestamp problem

The raw air quality data has a column literally called `timestamp`, which is a reserved
word in SQL and kept causing parse errors. We quote it and rename it to `datetime` inside
`stg_air_quality_hourly`, so nothing downstream has to deal with it. Small thing, but it
would break a build if you missed it.

## Why air quality is mostly null in the fact table

Open-Meteo only returns air quality for the forecast window (the next few days), not for
the 90 days of history we pulled for weather. So when we left join air quality onto the
daily weather in `fct_city_weather_day`, most of the older days come back null on the air
quality columns. We used a left join on purpose: we want to keep every weather day, and
let air quality fill in only where it exists, rather than throwing away history.

## Inner join for forecast vs actual

For `int_forecast_vs_actual` we used an inner join instead of a left join, because we only
care about dates where we have both a forecast and a real observation to compare. From a
single extraction run that overlap is basically just the current day, so
`mart_forecast_accuracy` is thin right now. If we ran the extraction repeatedly over
several days it would build up a real accuracy history. We left this as a known limitation
rather than pretending the comparison is richer than it is.

## Materialization

| Layer | Strategy | Why |
|-------|----------|-----|
| Staging | view | light pass-through, no reason to store it |
| Intermediate | view | only the marts read these |
| Marts | table | the dashboard hits these over and over, so we materialize once instead of recomputing a chain of views on every filter click |

## Comfort score

We defined a "comfortable" day as mean temperature between 18 and 26 C, under 1 mm of rain,
and wind under 25 km/h. `comfort_score` is just the percent of observed days per city that
hit all three. It is our own rough proxy, not an official standard, but it makes the city
ranking easy to read.

## Tests

Beyond the usual `unique` and `not_null` on the keys, we added tests that check real rules:

- temperature has to sit in a sane range (`accepted_range`)
- a day's minimum temperature can never be above its maximum (singular test)
- precipitation can never be negative (`accepted_range`, min 0)
- `comfort_score` has to be between 0 and 100 (`accepted_range`)
- the fact table has to be unique per city and day (`unique_combination_of_columns`)
- `city_name` in the fact table has to exist in `dim_location` (`relationships`)

The point was to test things that would actually catch a real modeling mistake, not just
tick the boxes.

## What we know is weak

- Forecast accuracy is thin from a single extraction run (see the inner join note).
- Air quality only covers the forecast horizon, so historical air quality is missing.
- The comfort thresholds are our own choice, so the ranking is only as meaningful as that definition.
