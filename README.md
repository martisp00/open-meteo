# Weather Analytics Engineering — Group Project

End-to-end analytics pipeline using Open-Meteo API, DuckDB, dbt Core, and Streamlit.

## Stack

- **Python** — data extraction from Open-Meteo APIs
- **DuckDB** — local analytical database
- **dbt Core** — transformation layer (staging → intermediate → marts)
- **Streamlit** — dashboard

## Setup

```bash
# 1. Install dependencies
uv sync        # or: pip install -r requirements.txt

# 2. Extract raw data
python scripts/extract_open_meteo.py --cities Madrid Barcelona Valencia

# 3. Load data into DuckDB
python create_db.py

# 4. Run dbt
dbt deps
dbt build

# 5. Launch dashboard
streamlit run dashboard/app.py
```

## Project Structure

```
group-weather-analytics/
├── scripts/            # Extraction scripts (Open-Meteo APIs)
├── data/raw/           # Raw CSV files (gitignored)
├── models/
│   ├── staging/        # stg_* — clean raw sources
│   ├── intermediate/   # int_* — joins and enrichments
│   └── marts/          # dim_* and fct_* — final analytics tables
├── dashboard/          # Streamlit app
├── tests/              # Custom dbt tests
├── seeds/              # Static reference data
├── macros/             # Reusable dbt macros
└── docs/               # Modeling decisions and documentation
```

## Team Members

- Mateus
- Teresa
- Francisco
- Marti

## Data Sources

| API | Description |
|-----|-------------|
| Geocoding | City → coordinates |
| Forecast | 7-day daily forecast |
| Historical Weather | Past 30 days daily weather |
| Air Quality | Hourly AQI metrics |
