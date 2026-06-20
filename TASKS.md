# Group Project — Remaining Tasks

Track progress here. Move items to **Done** when merged to master.

---

## Ingestion (scripts/)

- [ ] Agree on final city list and re-run `scripts/extract_open_meteo.py --cities ...`
- [ ] Add a `.env` or `config.py` for shared config (city list, past_days, forecast_days) so everyone uses the same settings

---

## Staging layer (models/staging/)

All four staging models currently pass through raw columns with no transformation.
Each one needs:

- [ ] **`stg_locations.sql`** — select only needed columns, cast types, add surrogate key with `dbt_utils.generate_surrogate_key`
- [ ] **`stg_weather_daily.sql`** — cast `date` to `date`, rename verbose column names if desired, drop `source_name`/`extracted_at`
- [ ] **`stg_forecast_daily.sql`** — same treatment as weather; keep `source_name` so forecast rows are distinguishable after joins
- [ ] **`stg_air_quality_hourly.sql`** — cast `timestamp` to `timestamp`, drop duplicates (the API can return the same hour twice across extraction runs)
- [ ] **`stg_locations.sql` dedup** — add `qualify row_number() over (partition by location_id order by extracted_at desc) = 1` to ensure one row per city

---

## Intermediate layer (models/intermediate/)

- [ ] **`int_air_quality_daily.sql`** — add `avg_pm10`, `max_aqi`, consider adding `carbon_monoxide` and `nitrogen_dioxide` averages; add `location_id` so downstream joins don't rely on `city_name` strings
- [ ] **`int_forecast_vs_actual.sql`** — also compare `temperature_2m_min` and `precipitation_sum`; add `abs(temp_error)` as a column for easier downstream aggregation
- [ ] **`int_weather_flags.sql`** — review thresholds (35°C heat, 20mm rain) with the group; consider adding a `is_cold_day` flag

---

## Mart layer (models/marts/)

- [ ] **`dim_location.sql`** — add `population` and `elevation` columns from `stg_locations`; add a surrogate key as the primary key
- [ ] **`fct_city_weather_day.sql`** — add `avg_pm10`, `max_aqi` from `int_air_quality_daily`; add `location_id` foreign key referencing `dim_location`
- [ ] **`mart_forecast_accuracy.sql`** — add `min_temp_error` and `avg_temp_error` columns alongside `mae_temp`
- [ ] Add a new mart: **`mart_city_comfort_score.sql`** — composite score combining temperature, precipitation, and AQI into a daily comfort index per city

---

## Tests (models/**/docs/*.yml + tests/)

- [ ] `dim_location`: `unique` + `not_null` on the primary key
- [ ] `fct_city_weather_day`: `unique` on `(city_name, date)`, `not_null` on `city_name` and `date`
- [ ] `fct_city_weather_day`: relationship test — `city_name` must exist in `dim_location`
- [ ] `stg_weather_daily` + `stg_forecast_daily`: `accepted_values` or range check on `temperature_2m_max` (e.g. between -50 and 60)
- [ ] `mart_forecast_accuracy`: `not_null` on `mae_temp`, check `mae_temp >= 0`

---

## Dashboard (dashboard/app.py)

- [ ] Add a **date range filter** (start date / end date) applied to `fct_city_weather_day`
- [ ] Add an **air quality chart** — daily AQI or PM2.5 trend for selected city
- [ ] Add a **city comparison chart** — e.g. temperature_2m_max across all cities on the same chart
- [ ] Improve layout — use `st.columns` to put filters side by side
- [ ] Add deployment instructions to `README.md` (local run + optional Streamlit Community Cloud)

---

## Documentation

- [ ] Fill in column descriptions in `models/intermediate/docs/intermediate.yml` and `models/marts/docs/marts.yml` (currently empty stubs)
- [ ] Update `README.md` with end-to-end setup steps: install deps → extract → load → dbt run → dbt test → streamlit
- [ ] Add a DAG diagram screenshot to `docs/` after `dbt docs generate`

---

## Done

- [x] Project skeleton (directories, dbt_project.yml, profiles.yml, packages.yml)
- [x] Extraction script (`scripts/extract_open_meteo.py`) — pulls 4 CSV files from Open-Meteo API
- [x] DuckDB loader (`scripts/load_to_duckdb.py`) — loads CSVs into `main` schema
- [x] `models/sources.yml` — wires raw DuckDB tables as dbt sources
- [x] Stub staging, intermediate, and mart models
- [x] Fixed column name bug: `datetime` → `timestamp` in `int_air_quality_daily.sql` and `staging.yml`
- [x] Fixed dashboard DB path to resolve correctly regardless of run directory
- [x] `requirements.txt` added
