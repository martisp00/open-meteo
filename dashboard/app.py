import os

import duckdb
import pandas as pd
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "my_database.duckdb")

st.set_page_config(page_title="Weather Analytics", layout="wide")
st.title("Weather Analytics Dashboard")

@st.cache_data
def load_data(query: str) -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(query).df()
    con.close()
    return df

# --- Filters ---
cities_df = load_data("select city_name from dim_location order by city_name")
selected_city = st.selectbox("City", cities_df["city_name"].tolist())

# --- Charts ---
weather_df = load_data(f"""
    select date, temperature_2m_max, temperature_2m_min, precipitation_sum
    from fct_city_weather_day
    where city_name = '{selected_city}'
    order by date
""")

st.subheader("Temperature over time")
st.line_chart(weather_df.set_index("date")[["temperature_2m_max", "temperature_2m_min"]])

st.subheader("Daily precipitation")
st.bar_chart(weather_df.set_index("date")["precipitation_sum"])

accuracy_df = load_data("select * from mart_forecast_accuracy order by mae_temp")
st.subheader("Forecast accuracy by city (MAE °C)")
st.dataframe(accuracy_df, use_container_width=True)
