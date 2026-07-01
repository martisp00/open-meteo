# Weather Analytics Engineering: Group Project

An end-to-end analytics pipeline that pulls live weather and air quality data for eight European cities from the Open-Meteo API and turns it into a clean, tested dbt project with an interactive Streamlit dashboard.

The question it answers: **which cities are the best places to be, weighing both comfort and air quality?** The finding is that the two do not move together. The most comfortable city is not automatically the one with the cleanest air.

## Architecture

```mermaid
flowchart LR
    A["Open-Meteo APIs"] -->|"extract_open_meteo.py"| B["CSV files"]
    B -->|"load_to_duckdb.py"| C[("DuckDB")]
    C --> D["staging (stg_)"]
    D --> E["intermediate (int_)"]
    E --> F["marts (dim / fct / mart_)"]
    F --> G["Streamlit dashboard"]
```

Data flows one way through three dbt layers:

- **Staging (`stg_`)** cleans each raw source one-to-one: renames columns, casts types, drops extraction metadata. No joins.
- **Intermediate (`int_`)** holds the real logic: aggregating hourly air quality to daily, adding weather flags, joining forecast to actuals.
- **Marts (`dim_`, `fct_`, `mart_`)** are the business-ready tables the dashboard reads.

## Stack

| Layer | Tool |
|---|---|
| Extraction | Python, Open-Meteo APIs |
| Storage | DuckDB |
| Transformation | dbt Core |
| Dashboard | Streamlit, Altair, PyDeck |

## What makes this more than a tutorial

- **Dimensional modeling.** A `dim_location` dimension and a `fct_city_weather_day` fact, split on purpose so a small, stable city table joins onto a big, growing measurements table.
- **Source freshness.** `dbt source freshness` checks the three time-series sources (warn after 24h, error after 48h). City coordinates are static reference data and are deliberately left out, the difference between refreshing facts and static reference data is the whole point.
- **A dashboard exposure.** The Streamlit app is declared as a dbt exposure, so it shows up at the end of the lineage graph and you can run `dbt build --select +exposure` to build everything it depends on before a refresh.
- **Tests that catch real mistakes.** The four generic tests, plus a singular test (a day's minimum temperature can never exceed its maximum), range tests (precipitation and error metrics can't go negative), and a uniqueness test on the fact grain.

## The dbt models

| Model | Layer | Grain | Used for |
|---|---|---|---|
| `stg_locations` | staging | one row per city | clean city reference |
| `stg_weather_daily` | staging | one row per city per day | clean daily weather |
| `stg_forecast_daily` | staging | one row per city per day | clean forecast |
| `stg_air_quality_hourly` | staging | one row per city per hour | clean air quality |
| `int_weather_flags` | intermediate | per city per day | heat / rain / wind / comfort flags |
| `int_air_quality_daily` | intermediate | per city per day | hourly air quality rolled to daily |
| `int_forecast_vs_actual` | intermediate | per city per day | forecast joined to actuals |
| `dim_location` | mart | one row per city | the map and joins |
| `fct_city_weather_day` | mart | one row per city per day | temperature, precipitation, detail |
| `mart_city_comfort` | mart | one row per city | comfort ranking and the overview |
| `mart_air_quality_summary` | mart | one row per city | air quality ranking and the overview |
| `mart_city_risk` | mart | one row per city | a weather risk score |
| `mart_monthly_weather` | mart | one row per city per month | seasonal trends |
| `mart_forecast_accuracy` | mart | one row per city | forecast accuracy |

Full reasoning per model lives in `docs/modeling_choices.md`.

## The dashboard

Launch it with `streamlit run dashboard/app.py`. It has:

- a map of the eight cities, colored by comfort;
- a comfort vs air quality overview that leads with the main insight;
- a comfort ranking with a metric selector;
- per-city detail (temperature and precipitation over a chosen date range);
- monthly weather trends across all cities;
- an air quality ranking colored by band, with a PM2.5 / PM10 table; and
- a forecast accuracy table.

## Setup

Run all commands from the project root.

```bash
# 1. Create and activate a virtual environment
uv venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Extract raw data from Open-Meteo
python scripts/extract_open_meteo.py

# 4. Load the CSV files into DuckDB
python scripts/load_to_duckdb.py

# 5. Point dbt at the local profile, install packages, build and test
# Windows PowerShell:
$env:DBT_PROFILES_DIR = "."
# macOS / Linux:
# export DBT_PROFILES_DIR=.
dbt deps
dbt build

# 6. Launch the dashboard
streamlit run dashboard/app.py
```

## Known limitations (and why)

We left these honest rather than papering over them:

- **Air quality only covers the forecast window.** Open-Meteo returns air quality for the next few days, not the 90 days of history, so historical air quality is missing by design.
- **Forecast accuracy is thin from a single extraction run.** Forecast and actuals only overlap on about one day per city per run. The loader does CREATE OR REPLACE on every run, so re-running extraction does not accumulate history on its own. To build a real accuracy record we would persist each run's forecast instead of replacing it, for example by appending runs or capturing them with a dbt snapshot.
- **The comfort thresholds are our own choice.** "Comfortable" means mild, dry, and calm by our definition, so the ranking is only as meaningful as that definition.

## Team

Francisco Javier Concha Bambach, Mateus Carneiro, Maria Teresa Ghirardi, and Martí Solà Puig.

## AI Acknowledgement

This project’s architecture, dimensional modeling, and business logic were entirely driven by the team. We integrated Claude (Anthropic) into our workflow strictly as a technical accelerator. 

- **What the AI handled:** Drafting boilerplate Python for data extraction, generating initial dbt model syntax, writing baseline YAML tests, and scaffolding the Streamlit dashboard components.
- **What the team owned:** Defining the data grain, structuring the dbt DAG (staging, intermediate, marts), determining the data quality testing strategy, and making all final analytical decisions (such as the comfort thresholds and forecast vs. actuals logic).

Every piece of AI-assisted code was rigorously reviewed, heavily modified, and tested by the team to ensure it met strict analytics engineering standards.