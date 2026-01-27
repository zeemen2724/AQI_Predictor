import streamlit as st
import pandas as pd
from utils import load_latest_data, load_model, get_latest_aqi

st.set_page_config(page_title="AQI Predictor", layout="wide")

st.title("🌫️ Karachi AQI Dashboard")

# Load data
df = load_latest_data()

# Current AQI
ts, aqi = get_latest_aqi(df)
st.metric("Current AQI", round(aqi, 2), help=f"Last updated: {ts}")

# Trend
st.subheader("📈 AQI Trend (Last 7 Days)")
df_7d = df.tail(24 * 7)
st.line_chart(df_7d.set_index("timestamp")["aqi"])

# Prediction
st.subheader("🔮 AQI Prediction (Next 3 Days)")
model = load_model()

future_df = df.tail(24 * 3).copy()
preds = model.predict(future_df.drop(columns=["aqi", "timestamp", "event_id"]))

future_df["prediction"] = preds
st.line_chart(future_df.set_index("timestamp")["prediction"])
