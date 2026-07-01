# Group Project — Remaining Tasks

Track progress here. Move items to **Done** when merged to master.
> **Update (master merge):** A full pipeline now lives on `master` (staging, intermediate, marts, tests, dashboard, docs). Items genuinely finished are ticked below. The rest are still open and are the real next tasks. Mateus's `scripts/load_to_duckdb.py` and this file were folded into master.

---

## Reconciliation (July 1) — status of the remaining unchecked items

The pipeline on `master` is complete and delivered. The unchecked boxes further down are **not** forgotten work. Each one is either done-but-never-ticked, deliberately superseded by a better decision, or explicitly out of scope. The source of truth for the final design is `README.md` and `docs/modeling_choices.md`.

**✅ Done, just never ticked below**
- Agree on final city list, and add `config.py` for shared config (city list, past_days, forecast_days). Shipped.
- `int_air_quality_daily`: `avg_pm10` added.
- `dim_location`: `population` and `elevation` added.
- `fct_city_weather_day`: `avg_pm10` added.

**🔁 Superseded on purpose (defensible design decisions)**
- `stg_locations` / `dim_location` surrogate key: we use `location_id` from the geocoding API as a natural key. It is tested `unique` + `not_null`, so a surrogate key would add nothing.
- `stg_locations` and `stg_air_quality_hourly` dedup: the loader does `CREATE OR REPLACE TABLE` on every run, so duplicate rows across extraction runs cannot exist. The `fct` grain test would catch them if they ever did. Those dedup items assumed an append-style loader we did not build.
- `location_id` foreign key on `fct_city_weather_day` / propagation into intermediate: referential integrity is instead provided by a `relationships` test on `city_name`, which is `unique` in `dim_location`. String joins are safe here.
- `int_weather_flags`: `is_cold_day` was replaced by `is_freezing_day`.
- `mart_city_comfort_score.sql` (composite score blending AQI into comfort): **deliberately not built.** We use `mart_city_comfort`, which keeps air quality OUT of the comfort score. Baking AQI into comfort would destroy our central finding, that comfort and air quality do not correlate. Keeping them separate was analytically necessary.

**📋 Genuinely open, low value / nice-to-have (out of scope for this deliverable)**
- `int_forecast_vs_actual`: min-temp and precipitation comparison (we shipped max-temp error).
- `mart_forecast_accuracy`: `min_temp_error` / `avg_temp_error` (we shipped `max_temp_error` and `mae_temp`).
- `mart_forecast_accuracy`: `not_null` on `mae_temp` (the `accepted_range` test already ignores nulls, and the SQL makes a null near-impossible).
- Streamlit Community Cloud deploy instructions (local run instructions are done; the cloud deploy itself is deferred).
- DAG diagram screenshot in `docs/` after `dbt docs generate`.


---

## Ingestion (scripts/)

- [ ] Agree on final city list and re-run `scripts/extract_open_meteo.py --cities ...`
- [ ] Add a `.env` or `config.py` for shared config (city list, past_days, forecast_days) so everyone uses the same settings

---

## Staging layer (models/staging/)

All four staging models currently pass through raw columns with no transformation.
Each one needs:

- [ ] **`stg_locations.sql`** — select only needed columns, cast types, add surrogate key with `dbt_utils.generate_surrogate_key`
- [x] **`stg_weather_daily.sql`** — cast `date` to `date`, rename verbose column names if desired, drop `source_name`/`extracted_at`
- [x] **`stg_forecast_daily.sql`** — same treatment as weather; keep `source_name` so forecast rows are distinguishable after joins
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

- [x] `dim_location`: `unique` + `not_null` on the primary key
- [x] `fct_city_weather_day`: `unique` on `(city_name, date)`, `not_null` on `city_name` and `date`
- [x] `fct_city_weather_day`: relationship test — `city_name` must exist in `dim_location`
- [x] `stg_weather_daily` + `stg_forecast_daily`: `accepted_values` or range check on `temperature_2m_max` (e.g. between -50 and 60)
- [ ] `mart_forecast_accuracy`: `not_null` on `mae_temp`, check `mae_temp >= 0`

---

## Dashboard (dashboard/app.py)

- [x] Add a **date range filter** (start date / end date) applied to `fct_city_weather_day`
- [x] Add an **air quality chart** — daily AQI or PM2.5 trend for selected city
- [x] Add a **city comparison chart** — e.g. temperature_2m_max across all cities on the same chart
- [x] Improve layout — use `st.columns` to put filters side by side
- [ ] Add deployment instructions to `README.md` (local run + optional Streamlit Community Cloud)

---

## Documentation

- [x] Fill in column descriptions in `models/intermediate/docs/intermediate.yml` and `models/marts/docs/marts.yml` (currently empty stubs)
- [x] Update `README.md` with end-to-end setup steps: install deps → extract → load → dbt run → dbt test → streamlit
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


---

## Also done on master (beyond the original list)

- [x] `mart_city_comfort.sql` — per-city comfort ranking (% of mild, dry, calm days)
- [x] Singular test: a day's min temperature can never exceed its max
- [x] `accepted_range` test: precipitation can never be negative
- [x] `accepted_range` test: comfort_score must be between 0 and 100
- [x] Dashboard: city map + rank-by-metric selector
- [x] `docs/modeling_choices.md` rewritten with full reasoning per layer
