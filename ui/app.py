import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    load_latest_data,
    load_model,
    get_latest_aqi,
    aqi_category
)

# ----------------------------------
# Page config
# ----------------------------------
st.set_page_config(
    page_title="Karachi AQI Dashboard",
    layout="wide",
    page_icon="🌫️"
)

# ----------------------------------
# Custom CSS
# ----------------------------------
st.markdown("""
<style>
/* Dark theme base */
.stApp {
    background-color: #1a1a2e;
}
body {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
.hero {
    padding: 2.5rem 3rem;
    border-radius: 16px;
    background: linear-gradient(90deg, #a855f7 0%, #ec4899 50%, #f97316 100%);
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.hero h1 {
    font-size: 1.8rem;
    font-weight: 600;
    margin: 0;
    margin-bottom: 0.3rem;
    color: white;
}
.hero p {
    font-size: 0.95rem;
    margin: 0;
    opacity: 0.95;
    color: white;
}
.card {
    background: #16213e;
    padding: 1.8rem;
    border-radius: 16px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
    margin-bottom: 1.5rem;
}
.small-card {
    background: #16213e;
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
    text-align: center;
}
.small-card h4 {
    font-size: 0.85rem;
    color: #9ca3af;
    margin: 0 0 0.5rem 0;
    font-weight: 500;
}
.small-card h2 {
    font-size: 2rem;
    margin: 0.3rem 0;
    font-weight: 700;
}
.small-card p {
    font-size: 0.9rem;
    margin: 0.3rem 0 0 0;
    color: #9ca3af;
}
.stPlotlyChart {
    background: transparent !important;
}
/* Streamlit element overrides */
h1, h2, h3, h4, h5, h6 {
    color: #e0e0e0 !important;
}
p {
    color: #b0b0b0;
}
.stMarkdown {
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Load data + model
# ----------------------------------
df = load_latest_data()
model = load_model()

# ----------------------------------
# HERO HEADER
# ----------------------------------
st.markdown("""
<div class="hero">
    <h1>Karachi Air Quality Dashboard</h1>
    <p>Live AI-powered air pollution insights & forecasts</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# CURRENT AQI
# ----------------------------------
ts, aqi = get_latest_aqi(df)
status, _ = aqi_category(aqi)

aqi_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=aqi,
    number={"suffix": " AQI", "font": {"size": 42, "color": "#ef4444"}},
    title={"text": "<span style='color: #e0e0e0;'>Current Air Quality</span><br><span style='font-size:12px; color:#9ca3af'>Last updated: Just now</span>", 
           "font": {"size": 16}},
    gauge={
        "axis": {"range": [0, 400], "tickwidth": 1, "tickcolor": "#4a5568", "tickfont": {"color": "#9ca3af"}},
        "bar": {"color": "#ef4444", "thickness": 0.75},
        "bgcolor": "#16213e",
        "borderwidth": 0,
        "steps": [
            {"range": [0, 50], "color": "#064e3b"},
            {"range": [50, 100], "color": "#713f12"},
            {"range": [100, 150], "color": "#7c2d12"},
            {"range": [150, 200], "color": "#7f1d1d"},
            {"range": [200, 300], "color": "#581c87"},
            {"range": [300, 400], "color": "#450a0a"},
        ],
        "threshold": {
            "line": {"color": "#ef4444", "width": 4},
            "thickness": 0.75,
            "value": aqi
        }
    },
))
aqi_gauge.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=80, b=20),
    paper_bgcolor="#16213e",
    plot_bgcolor="#16213e",
    font={"family": "Arial, sans-serif", "color": "#e0e0e0"}
)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.plotly_chart(aqi_gauge, use_container_width=True)
st.markdown(f"""
<div style='text-align: center; margin-top: -20px;'>
    <p style='font-size: 1.1rem; font-weight: 600; color: #ef4444; margin: 0;'>{status}</p>
    <p style='font-size: 0.85rem; color: #9ca3af; margin-top: 8px;'>
        Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.
    </p>
    <p style='font-size: 0.75rem; color: #6b7280; margin-top: 12px;'>
        <em>Based on health advisory: 🟢 Good  🟡 Moderate  🟠 Unhealthy for Sensitive  🔴 Unhealthy  🟣 Very Unhealthy  🔴 Hazardous</em>
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# PAST WEEK HEATMAP
# ----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin: 0 0 0.3rem 0; color: #e0e0e0;'>📊 Past Week Air Quality Patterns</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 0.9rem; margin-top: 0;'>Hourly AQI breakdown across days</p>", unsafe_allow_html=True)

df_7d = df.tail(24 * 7).copy()
df_7d["hour"] = df_7d["timestamp"].dt.hour
df_7d["day"] = df_7d["timestamp"].dt.day_name()

# Reorder days properly
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_7d["day"] = pd.Categorical(df_7d["day"], categories=day_order, ordered=True)

heatmap = px.density_heatmap(
    df_7d,
    x="hour",
    y="day",
    z="aqi",
    color_continuous_scale=["#22c55e", "#eab308", "#fb923c", "#ef4444", "#a855f7"],
    labels={"hour": "Hour of Day", "day": "Day", "aqi": "AQI"},
)
heatmap.update_layout(
    height=250,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="#16213e",
    plot_bgcolor="#16213e",
    font={"family": "Arial, sans-serif", "size": 11, "color": "#e0e0e0"},
    xaxis=dict(gridcolor="#2d3748", tickfont=dict(color="#9ca3af")),
    yaxis=dict(gridcolor="#2d3748", tickfont=dict(color="#9ca3af"))
)
heatmap.update_xaxes(side="bottom")

st.plotly_chart(heatmap, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------
# FORECAST
# ----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin: 0 0 0.3rem 0; color: #e0e0e0;'>🔮 AI Forecast Horizon</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af; font-size: 0.9rem; margin-top: 0;'>Next 72 hrs predicted AQI levels</p>", unsafe_allow_html=True)

future = df.tail(72).copy()
preds = model.predict(
    future.drop(columns=["aqi", "timestamp", "event_id"])
)

future["Predicted AQI"] = preds

# Create gradient colors based on AQI values
colors_list = []
for val in preds:
    if val <= 50:
        colors_list.append("#fbbf24")
    elif val <= 100:
        colors_list.append("#fb923c")
    elif val <= 150:
        colors_list.append("#f97316")
    elif val <= 200:
        colors_list.append("#ef4444")
    else:
        colors_list.append("#dc2626")

forecast_fig = go.Figure(data=[
    go.Bar(
        x=future["timestamp"],
        y=future["Predicted AQI"],
        marker=dict(
            color=future["Predicted AQI"],
            colorscale=[[0, "#fbbf24"], [0.5, "#fb923c"], [1, "#ef4444"]],
            showscale=False
        ),
        hovertemplate='<b>%{x}</b><br>AQI: %{y:.0f}<extra></extra>'
    )
])

forecast_fig.update_layout(
    height=300,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="#16213e",
    plot_bgcolor="#16213e",
    xaxis=dict(showgrid=False, title="", tickfont=dict(color="#9ca3af")),
    yaxis=dict(
        showgrid=True, 
        gridcolor="#2d3748", 
        title=dict(text="AQI", font=dict(color="#e0e0e0")), 
        tickfont=dict(color="#9ca3af")
    ),
    font={"family": "Arial, sans-serif", "color": "#e0e0e0"}
)

st.plotly_chart(forecast_fig, use_container_width=True)

# Daily summary cards
st.write("")
cols = st.columns(3)
for i, col in enumerate(cols):
    day_avg = preds[i*24:(i+1)*24].mean()
    label, _ = aqi_category(day_avg)
    
    # Color based on AQI
    if day_avg <= 50:
        color = "#22c55e"
    elif day_avg <= 100:
        color = "#eab308"
    elif day_avg <= 150:
        color = "#fb923c"
    elif day_avg <= 200:
        color = "#ef4444"
    else:
        color = "#a855f7"

    col.markdown(f"""
    <div class="small-card">
        <h4>Day {i+1}</h4>
        <h2 style='color: {color};'>{day_avg:.0f}</h2>
        <p>{label}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

