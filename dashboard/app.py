"""Streamlit dashboard for the Weather Analytics group project.

Reads from the final dbt mart models in DuckDB. Run from the project root:
    streamlit run dashboard/app.py
"""

from pathlib import Path
import altair as alt
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
# The big picture: comfort vs air quality
# ---------------------------------------------------------------------------
st.header("The big picture: comfort vs air quality")
st.caption("Each city is placed by comfort (right is more comfortable, over 90 days) and air quality (up is cleaner, over the recent forecast window). Cities toward the top right are strong on both. The two do not move together, so the most comfortable city is not automatically the one with the cleanest air.")
overview = run_query(
    """
    select c.city_name, c.comfort_score, a.avg_aqi, a.aqi_category
    from mart_city_comfort c
    join mart_air_quality_summary a on c.city_name = a.city_name
    """
)
# Valencia is our headline city: the most comfortable in the study, so it is the
# sharpest test of "is the comfiest city also the cleanest?". Coral makes it pop.
is_valencia = alt.datum.city_name == "Valencia"

# Fixed axis ranges (data + a little padding) so the four quadrant labels sit in the corners.
pad_x, pad_y = 4, 3
cx_min = float(overview["comfort_score"].min()) - pad_x
cx_max = float(overview["comfort_score"].max()) + pad_x
ay_min = float(overview["avg_aqi"].min()) - pad_y
ay_max = float(overview["avg_aqi"].max()) + pad_y
xscale = alt.Scale(domain=[cx_min, cx_max])
yscale = alt.Scale(domain=[ay_min, ay_max], reverse=True)  # reversed so cleaner air is up

# Two dashed guide lines at the average comfort and average AQI split the chart into four quadrants.
mean_comfort = float(overview["comfort_score"].mean())
mean_aqi = float(overview["avg_aqi"].mean())
vline = alt.Chart(pd.DataFrame({"x": [mean_comfort]})).mark_rule(
    color="#5b6b7d", strokeDash=[4, 4], size=1).encode(x=alt.X("x:Q", scale=xscale))
hline = alt.Chart(pd.DataFrame({"y": [mean_aqi]})).mark_rule(
    color="#5b6b7d", strokeDash=[4, 4], size=1).encode(y=alt.Y("y:Q", scale=yscale))

# One small italic label tucked into each corner, so each region reads in plain English.
def corner_label(x, y, text, align, baseline):
    return alt.Chart(pd.DataFrame({"x": [x], "y": [y], "t": [text]})).mark_text(
        align=align, baseline=baseline, dx=(8 if align == "left" else -8),
        dy=(10 if baseline == "top" else -10), fontSize=16, fontStyle="italic", fontWeight=600, color="#aab6c4"
    ).encode(x=alt.X("x:Q", scale=xscale), y=alt.Y("y:Q", scale=yscale), text="t:N")
c1 = corner_label(cx_max, ay_min, "clean + comfortable", "right", "top")
c2 = corner_label(cx_max, ay_max, "comfortable, poor air", "right", "bottom")
c3 = corner_label(cx_min, ay_min, "clean, less comfortable", "left", "top")
c4 = corner_label(cx_min, ay_max, "poor air, less comfortable", "left", "bottom")

# Shade the four regions: teal = the win-win corner (comfortable + clean),
# red = the worst corner, and the two trade-off corners stay neutral dark
# (Valencia lives in one of them, so keeping it neutral lets Valencia pop).
quads = pd.DataFrame([
    {"x": mean_comfort, "x2": cx_max,       "y": ay_min,   "y2": mean_aqi, "fill": "good"},
    {"x": cx_min,       "x2": mean_comfort, "y": mean_aqi, "y2": ay_max,   "fill": "bad"},
    {"x": cx_min,       "x2": mean_comfort, "y": ay_min,   "y2": mean_aqi, "fill": "mixed"},
    {"x": mean_comfort, "x2": cx_max,       "y": mean_aqi, "y2": ay_max,   "fill": "mixed"},
])
rects = alt.Chart(quads).mark_rect(opacity=0.16).encode(
    x=alt.X("x:Q", scale=xscale), x2="x2:Q",
    y=alt.Y("y:Q", scale=yscale), y2="y2:Q",
    color=alt.Color("fill:N",
        scale=alt.Scale(domain=["good", "bad", "mixed"], range=["#14b8a6", "#ef4444", "#1e293b"]),
        legend=None),
)

# Neutral dots for every city; coral and bigger for Valencia so it stays the hero.
overview_points = (
    alt.Chart(overview).mark_circle(opacity=0.95, stroke="#0e1117", strokeWidth=0.6).encode(
        x=alt.X("comfort_score:Q", title="Comfort score  (right is more comfortable)", scale=xscale,
                axis=alt.Axis(titleFontSize=15)),
        y=alt.Y("avg_aqi:Q", title="Air quality, AQI  (up is cleaner)", scale=yscale,
                axis=alt.Axis(titleFontSize=15)),
        color=alt.condition(is_valencia, alt.value("#FF5C3A"), alt.value("#cbd5e1")),
        size=alt.condition(is_valencia, alt.value(520), alt.value(190)),
        tooltip=["city_name", "comfort_score", "avg_aqi", "aqi_category"],
    )
)
overview_labels = (
    alt.Chart(overview).mark_text(dy=-20, fontSize=14).encode(
        x=alt.X("comfort_score:Q", scale=xscale),
        y=alt.Y("avg_aqi:Q", scale=yscale),
        text="city_name:N",
        color=alt.condition(is_valencia, alt.value("#FF5C3A"), alt.value("#e2e8f0")),
    )
)
st.altair_chart((rects + vline + hline + c1 + c2 + c3 + c4 + overview_points + overview_labels).properties(height=470, width="container"))

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
           precipitation_sum
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

# ---------------------------------------------------------------------------
# Monthly weather trends
# ---------------------------------------------------------------------------
st.header("Monthly weather trends")
st.caption("Average temperature per city per month, so you can watch the season build across the period. Hover a point for that month's detail.")
monthly = run_query(
    """
    select city_name, month, avg_temp, min_temp, max_temp, total_precipitation, comfortable_days
    from mart_monthly_weather
    order by month, city_name
    """
)
monthly_chart = (
    alt.Chart(monthly)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y", tickCount={"interval": "month", "step": 1})),
        y=alt.Y("avg_temp:Q", title="Average temperature (C)"),
        color=alt.Color("city_name:N", title="City"),
        tooltip=["city_name", "month", "avg_temp", "min_temp", "max_temp", "total_precipitation"],
    )
    .properties(height=360, width="container")
)
st.altair_chart(monthly_chart)

# ---------------------------------------------------------------------------
# Air quality by city
# ---------------------------------------------------------------------------
st.header("Air quality by city")
st.caption("Average European AQI per city over the days we have air quality for, which is the forecast window (a few recent days). Lower is cleaner. Bars are colored by air quality band, and the table breaks out PM2.5 and PM10.")
air = run_query(
    """
    select city_name, avg_aqi, aqi_category, avg_pm2_5, avg_pm10, days_with_air_quality
    from mart_air_quality_summary
    order by avg_aqi
    """
)
aqi_order = ["Good", "Fair", "Moderate", "Poor"]
aqi_colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
aqi_chart = (
    alt.Chart(air)
    .mark_bar()
    .encode(
        x=alt.X("avg_aqi:Q", title="Average European AQI (lower is cleaner)"),
        y=alt.Y("city_name:N", sort="x", title=None),
        color=alt.Color(
            "aqi_category:N",
            scale=alt.Scale(domain=aqi_order, range=aqi_colors),
            legend=alt.Legend(title="AQI band"),
        ),
        tooltip=["city_name", "avg_aqi", "aqi_category", "avg_pm2_5", "avg_pm10", "days_with_air_quality"],
    )
    .properties(height=320, width="container")
)
st.altair_chart(aqi_chart)
st.dataframe(air, width="stretch")

# ---------------------------------------------------------------------------
# Forecast accuracy
# ---------------------------------------------------------------------------
st.header("Forecast accuracy by city")
st.caption("MAE = mean absolute error between forecast and actual max temperature, on overlapping dates only. From one extraction run that overlap is about a day per city, so this fills out if we re-run extraction over time.")
accuracy = run_query(
    "select city_name, days_compared, mae_temp, max_temp_error from mart_forecast_accuracy order by mae_temp"
)
st.dataframe(accuracy, width="stretch")
