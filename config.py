"""Shared extraction settings for the whole team.

Edit these in ONE place so everyone pulls the exact same data. The extraction
script reads these as its defaults, so running

    python scripts/extract_open_meteo.py

with no arguments uses whatever is set here. You can still override on the
command line if you need to (e.g. --cities Madrid for a quick test).
"""

# Cities to pull. Names must match what the Open-Meteo geocoding API expects.
CITIES = [
    "Madrid",
    "Barcelona",
    "Valencia",
    "Sevilla",
    "Bilbao",
    "Lisbon",
    "Porto",
    "Paris",
]

# Days of recent history to pull (allowed range: 0 to 92).
PAST_DAYS = 90

# Days of forecast to pull (allowed range: 1 to 16).
FORECAST_DAYS = 7
