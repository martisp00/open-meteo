"""Load the extracted Open-Meteo CSV files into DuckDB as raw source tables.

Run from the project root AFTER scripts/extract_open_meteo.py:
    python create_db.py
"""

from pathlib import Path
import duckdb

# The database file lives at the project root. dbt and the dashboard both read this.
DB_PATH = "my_database.duckdb"

# Folder where the extraction script wrote the raw CSVs.
RAW_DIR = Path("data/raw/open_meteo")

# Each CSV maps to the raw table name dbt expects (see models/sources.yml).
TABLES = {
    "raw_locations": "raw_locations.csv",
    "raw_weather_daily": "raw_weather_daily.csv",
    "raw_forecast_daily": "raw_forecast_daily.csv",
    "raw_air_quality_hourly": "raw_air_quality_hourly.csv",
}


def main() -> None:
    con = duckdb.connect(DB_PATH)
    for table_name, file_name in TABLES.items():
        csv_path = RAW_DIR / file_name
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing {csv_path}. Run the extraction script first.")
        # read_csv_auto figures out column types (dates, numbers, text) on its own.
        con.execute(
            f"create or replace table {table_name} as "
            f"select * from read_csv_auto('{csv_path.as_posix()}')"
        )
        count = con.execute(f"select count(*) from {table_name}").fetchone()[0]
        print(f"Loaded {table_name}: {count:,} rows")
    con.close()
    print(f"\nDone. Database written to {DB_PATH}")


if __name__ == "__main__":
    main()
