import streamlit as st
import pandas as pd

from utils import (
    load_latest_data,
    load_model,
    load_metrics,
    get_latest_aqi,
    aqi_category
)

st.set_page_config(page_title="AQI Predictor", layout="wide")
st.title("🌫️ Karachi AQI Dashboard")

# -----------------------
# Load data + model
# -----------------------
df = load_latest_data()
model = load_model()

# -----------------------
# Current AQI
# -----------------------
ts, aqi = get_latest_aqi(df)
status, color = aqi_category(aqi)

st.metric(
    label="🌫️ Current AQI",
    value=f"{round(aqi, 2)}",
    help=f"Last updated: {ts}"
)

st.markdown(
    f"<h3 style='color:{color}'>Status: {status}</h3>",
    unsafe_allow_html=True
)

# -----------------------
# AQI Trend
# -----------------------
st.subheader("📈 AQI Trend (Last 7 Days)")
df_7d = df.tail(24 * 7)
st.line_chart(df_7d.set_index("timestamp")["aqi"])

# -----------------------
# Prediction
# -----------------------
st.subheader("🔮 AQI Forecast (Next 72 Hours)")

future_df = df.tail(72).copy()
preds = model.predict(
    future_df.drop(columns=["aqi", "timestamp", "event_id"])
)

future_df["Predicted AQI"] = preds

st.line_chart(
    future_df.set_index("timestamp")[["Predicted AQI"]]
)

avg_future_aqi = preds.mean()
status, _ = aqi_category(avg_future_aqi)

st.info(
    f"📌 **Average predicted AQI:** {avg_future_aqi:.1f} → {status}"
)

# -----------------------
# Model Comparison
# -----------------------
st.subheader("🤖 Model Performance Comparison")

metrics = load_metrics()
metrics_df = pd.DataFrame(metrics).T.reset_index()
metrics_df.rename(columns={"index": "Model"}, inplace=True)

st.dataframe(metrics_df, width="stretch")  

st.bar_chart(
    metrics_df.set_index("Model")[["RMSE", "MAE"]]
)

best_model = metrics_df.loc[metrics_df["RMSE"].idxmin(), "Model"]

st.success(
    f"✅ **{best_model}** selected as final model because it has the lowest RMSE."
)

# -----------------------
# Pollutants
# -----------------------
st.subheader("🧪 Current Pollutant Levels")

latest = df.iloc[-1]

pollutants = [
    "pm2_5", "pm10", "carbon_monoxide",
    "nitrogen_dioxide", "sulphur_dioxide", "ozone"
]

pollutant_df = latest[pollutants].to_frame(name="Value")
st.bar_chart(pollutant_df)
