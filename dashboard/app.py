"""Streamlit dashboard for the Weather Analytics group project.

Reads from the final dbt mart models in DuckDB. Run from the project root:
    streamlit run dashboard/app.py
"""

from pathlib import Path
import duckdb
import pandas as pd
import pydeck as pdk
import streamlit as st

# Resolve the database at the project root, no matter where streamlit is launched from.
DB_PATH = str(Path(__file__).resolve().parent.parent / "my_database.duckdb")

st.set_page_config(page_title="Weather Analytics", layout="wide")


@st.cache_data
def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return con.execute(query, params).df()
    finally:
        con.close()


st.title("Weather Analytics Dashboard")
st.caption("Open-Meteo data modeled with dbt. Main model grain (fct_city_weather_day): one row per city per day.")

# ---------------------------------------------------------------------------
# Map of cities in the analysis
# ---------------------------------------------------------------------------
st.subheader("Cities in the analysis")
st.caption("Each dot is a city, colored by its comfort score. Greener is more comfortable, redder is less. Hover over a dot to see the city.")

map_data = run_query(
    """
    select l.city_name, c.country, l.latitude, l.longitude,
           round(c.comfort_score, 1) as comfort_score
    from dim_location l
    join mart_city_comfort c on l.city_name = c.city_name
    """
)

# Color each dot on a red to green scale based on comfort score,
# spread across the actual min and max so the difference is easy to see.
lo = map_data["comfort_score"].min()
hi = map_data["comfort_score"].max()
span = (hi - lo) or 1.0
norm = (map_data["comfort_score"] - lo) / span
map_data["r"] = ((1 - norm) * 215).astype(int)
map_data["g"] = (norm * 165).astype(int)
map_data["b"] = 70

st.pydeck_chart(
    pdk.Deck(
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position="[longitude, latitude]",
                get_fill_color="[r, g, b, 200]",
                get_radius=35000,
                radius_min_pixels=8,
                radius_max_pixels=20,
                pickable=True,
            )
        ],
        initial_view_state=pdk.ViewState(
            latitude=float(map_data["latitude"].mean()),
            longitude=float(map_data["longitude"].mean()),
            zoom=4,
        ),
        tooltip={"text": "{city_name}, {country}: comfort {comfort_score}"},
        map_style=pdk.map_styles.CARTO_DARK,
    )
)

# ---------------------------------------------------------------------------
# City ranking (with a metric selector)
# ---------------------------------------------------------------------------
st.header("City ranking")
st.caption("comfort_score = percent of observed days that were mild (18-26C mean), dry (<1mm), and calm (<25 km/h).")
comfort = run_query(
    """
    select city_name, country, days_observed, avg_temp, avg_precipitation,
           comfortable_days, heat_days, rainy_days, windy_days, comfort_score
    from mart_city_comfort
    """
)
metric_labels = {
    "comfort_score": "Comfort score (% comfortable days)",
    "comfortable_days": "Comfortable days",
    "heat_days": "Heat days (max >= 35C)",
    "rainy_days": "Heavy rain days (>= 20mm)",
    "windy_days": "Windy days (>= 40 km/h)",
    "avg_temp": "Average temperature (C)",
}
metric = st.selectbox("Rank cities by", list(metric_labels.keys()), format_func=lambda k: metric_labels[k])
ranked = comfort.sort_values(metric, ascending=False)
st.bar_chart(ranked.set_index("city_name")[metric])
st.dataframe(comfort.sort_values("comfort_score", ascending=False), width="stretch")

# ---------------------------------------------------------------------------
# Per-city detail, with filters
# ---------------------------------------------------------------------------
st.header("City detail")
cities = comfort.sort_values("comfort_score", ascending=False)["city_name"].tolist()
col1, col2 = st.columns([1, 2])
with col1:
    selected_city = st.selectbox("City", cities)

bounds = run_query(
    "select min(date) as min_d, max(date) as max_d from fct_city_weather_day where city_name = ?",
    (selected_city,),
)
min_d = pd.to_datetime(bounds["min_d"].iloc[0]).date()
max_d = pd.to_datetime(bounds["max_d"].iloc[0]).date()
with col2:
    date_range = st.slider("Date range", min_value=min_d, max_value=max_d, value=(min_d, max_d))

weather = run_query(
    """
    select date, temperature_2m_max, temperature_2m_min, temperature_2m_mean,
           precipitation_sum, wind_speed_10m_max, avg_aqi
    from fct_city_weather_day
    where city_name = ? and date between ? and ?
    order by date
    """,
    (selected_city, date_range[0], date_range[1]),
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg temp (C)", round(weather["temperature_2m_mean"].mean(), 1))
k2.metric("Hottest day (C)", round(weather["temperature_2m_max"].max(), 1))
k3.metric("Total rain (mm)", round(weather["precipitation_sum"].sum(), 1))
k4.metric("Days shown", len(weather))

st.subheader("Temperature over time")
st.line_chart(weather.set_index("date")[["temperature_2m_max", "temperature_2m_min"]])

st.subheader("Daily precipitation (mm)")
st.bar_chart(weather.set_index("date")["precipitation_sum"])

aq = weather.dropna(subset=["avg_aqi"])
st.subheader("Air quality (European AQI)")
st.caption("Open-Meteo only returns air quality for the forecast window, so this is short on purpose. Older days have no air quality data.")
if aq.empty:
    st.info("No air quality data in this date range. Air quality is only fetched for the forecast horizon.")
else:
    st.line_chart(aq.set_index("date")["avg_aqi"])

# ---------------------------------------------------------------------------
# Forecast accuracy
# ---------------------------------------------------------------------------
st.header("Forecast accuracy by city")
st.caption("MAE = mean absolute error between forecast and actual max temperature, on overlapping dates only. From one extraction run that overlap is about a day per city, so this fills out if we re-run extraction over time.")
accuracy = run_query(
    "select city_name, days_compared, mae_temp, max_temp_error from mart_forecast_accuracy order by mae_temp"
)
st.dataframe(accuracy, width="stretch")
