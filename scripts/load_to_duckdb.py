#!/usr/bin/env python3
"""Load raw Open-Meteo CSVs into DuckDB (main schema).

Run this after extract_open_meteo.py has produced the four CSV files:
    python scripts/load_to_duckdb.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

DB_PATH = Path(__file__).parent.parent / "my_database.duckdb"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "open_meteo"

TABLES = [
    "raw_locations",
    "raw_weather_daily",
    "raw_forecast_daily",
    "raw_air_quality_hourly",
]


def main() -> int:
    missing = [t for t in TABLES if not (RAW_DIR / f"{t}.csv").exists()]
    if missing:
        print(
            f"Missing CSV files in {RAW_DIR}: {missing}\n"
            "Run scripts/extract_open_meteo.py first.",
            file=sys.stderr,
        )
        return 1

    conn = duckdb.connect(str(DB_PATH))

    for table in TABLES:
        csv_path = (RAW_DIR / f"{table}.csv").as_posix()
        conn.execute(
            f"CREATE OR REPLACE TABLE main.{table} AS "
            f"SELECT * FROM read_csv_auto('{csv_path}')"
        )
        count = conn.execute(f"SELECT count(*) FROM main.{table}").fetchone()[0]
        print(f"Loaded {count:,} rows → main.{table}")

    conn.close()
    print(f"\nDatabase: {DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
