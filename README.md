# Weather Analytics Engineering - Group Project

End-to-end analytics pipeline using the Open-Meteo API, DuckDB, dbt Core, and Streamlit.

## Stack

- **Python** - data extraction from Open-Meteo APIs
- **DuckDB** - local analytical database
- **dbt Core** - transformation layer (staging -> intermediate -> marts)
- **Streamlit** - dashboard

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
python scripts/extract_open_meteo.py --cities Madrid Barcelona Valencia Sevilla Bilbao Lisbon Porto Paris --past-days 90 --forecast-days 7

# 4. Load the CSV files into DuckDB
python create_db.py

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

## Final models powering the dashboard

| Model | Grain | Used for |
|-------|-------|----------|
| `mart_city_comfort` | one row per city | City comfort ranking |
| `fct_city_weather_day` | one row per city per day | Temperature, precipitation, air quality charts |
| `mart_forecast_accuracy` | one row per city | Forecast accuracy table |

See `docs/modeling_choices.md` for the full modeling rationale.

## AI acknowledgement

This project was developed with the assistance of Claude (Anthropic). AI tools were used
to help generate and review the data loader, dbt models, tests, and the Streamlit
dashboard, and to explain modeling decisions. All code was reviewed and run by the team.

## Team

- Mateus
- Teresa
- Francisco
- Marti
